# Clipboard Content Editor: edit clipboard text before pasting
# Copyright (C) 2026 Fauzan January
# Released under GPL 2

import addonHandler
import api
import globalPluginHandler
import gui
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel, NVDASettingsDialog

import config
import tones
import ui
import wx
from scriptHandler import script

addonHandler.initTranslation()

class InfoDialog(wx.Dialog):
	def __init__(self, parent, title, content, url=None):
		super().__init__(parent, title=title, size=(600, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.url = url
		self.content = content
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.textCtrl = wx.TextCtrl(self, value=content, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
		sizer.Add(self.textCtrl, 1, wx.EXPAND | wx.ALL, 10)
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btnCopy = wx.Button(self, label=_("&Copy to Clipboard"))
		self.btnCopy.Bind(wx.EVT_BUTTON, self.onCopy)
		btnSizer.Add(self.btnCopy, 0, wx.ALL, 5)
		if self.url:
			self.btnOpen = wx.Button(self, label=_("&Open in Browser"))
			self.btnOpen.Bind(wx.EVT_BUTTON, self.onOpen)
			btnSizer.Add(self.btnOpen, 0, wx.ALL, 5)
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label=_("&Close"))
		btnSizer.Add(self.btnClose, 0, wx.ALL, 5)
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.BOTTOM, 10)
		self.SetSizer(sizer)
		self.Centre()
		self.textCtrl.SetFocus()

	def onCopy(self, event):
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(wx.TextDataObject(self.content))
			wx.TheClipboard.Close()
			ui.message(_("Text successfully copied."))
		else:
			ui.message(_("Failed to copy text."))

	def onOpen(self, event):
		if self.url:
			import webbrowser
			webbrowser.open(self.url)

ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]

confspec = {
	"protectModeEnabled": "boolean(default=True)",
	"backupLevels": "integer(default=1)",
	"soundEnabled": "boolean(default=True)",
	"historySize": "string(default='10')",
	"language": "string(default='default')",
}
config.conf.spec["ClipboardContentEditor"] = confspec

if "ClipboardContentEditor" not in config.conf:
	config.conf["ClipboardContentEditor"] = {}

try:
	lang = config.conf["ClipboardContentEditor"].get("language", "default")
	if lang != "default":
		import gettext
		import os
		import inspect
		addon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
		locale_dir = os.path.join(addon_dir, "locale")
		t = gettext.translation("nvda", localedir=locale_dir, languages=[lang])
		frame = inspect.currentframe()
		if frame:
			frame.f_globals["_"] = t.gettext
except Exception:
	pass


def _buildInformationMessage(text):
	charCount = len(text)
	wordCount = len(text.split())
	lineCount = len(text.splitlines()) if text else 0
	# Paragraphs are separated by empty lines (double newline)
	import re
	paraCount = len([p for p in re.split(r'\n\s*\n', text) if p.strip()]) if text else 0
	
	return _("Clipboard information: {chars} characters, {words} words, {lines} lines, {paras} paragraphs").format(
		chars=charCount,
		words=wordCount,
		lines=lineCount,
		paras=paraCount,
	)


def _playSound(hz, duration):
	if config.conf["ClipboardContentEditor"].get("soundEnabled", True):
		tones.beep(hz, duration)


def _announceClipboardEmpty():
	ui.message(_("Clipboard is empty"))


def _copyTextToClipboard(text):
	try:
		if text:
			return bool(api.copyToClip(text))
		if api.copyToClip(""):
			return True
	except Exception:
		pass
	try:
		if wx.TheClipboard.Open():
			try:
				wx.TheClipboard.SetData(wx.TextDataObject(""))
				return True
			finally:
				wx.TheClipboard.Close()
	except Exception:
		pass
	return False


def _isWordChar(ch):
	return ch.isalnum() or ch == "_"


def _isWordBoundary(fullText, start, end):
	if start > 0 and _isWordChar(fullText[start - 1]):
		return False
	if end < len(fullText) and _isWordChar(fullText[end]):
		return False
	return True


def _findNextMatch(fullText, findText, startIndex, wholeWordsOnly, ignoreCase=False):
	if ignoreCase:
		searchText = fullText.lower()
		searchFind = findText.lower()
	else:
		searchText = fullText
		searchFind = findText
	i = startIndex
	while True:
		idx = searchText.find(searchFind, i)
		if idx == -1:
			return None
		end = idx + len(findText)
		if not wholeWordsOnly or _isWordBoundary(fullText, idx, end):
			return idx, end
		i = idx + 1


def _findNext(fullText, findText, startIndex, matchCase, wholeWordsOnly):
	if matchCase:
		return _findNextMatch(fullText, findText, startIndex, wholeWordsOnly)
	return _findNextMatch(
		fullText,
		findText,
		startIndex,
		wholeWordsOnly,
		ignoreCase=True,
	)


def _matches(selection, findText, matchCase):
	if not matchCase:
		return selection.lower() == findText.lower()
	return selection == findText


def _selectionMatches(fullText, start, end, selection, findText, matchCase, wholeWordsOnly):
	if not selection:
		return False
	if not _matches(selection, findText, matchCase):
		return False
	if not wholeWordsOnly:
		return True
	return _isWordBoundary(fullText, start, end)


def _applyReplacementCase(selection, replaceText):
	letters = [ch for ch in selection if ch.isalpha()]
	if not letters:
		return replaceText
	if all(ch.isupper() for ch in letters):
		return replaceText.upper()
	if all(ch.islower() for ch in letters):
		return replaceText.lower()
	if letters[0].isupper():
		if not replaceText:
			return replaceText
		return replaceText.lower().capitalize()
	return replaceText


def _replaceAll(fullText, findText, replaceText, matchCase, wholeWordsOnly):
	if matchCase:
		searchText = fullText
		searchFind = findText
	else:
		searchText = fullText.lower()
		searchFind = findText.lower()
	parts = []
	count = 0
	i = 0
	while True:
		idx = searchText.find(searchFind, i)
		if idx == -1:
			parts.append(fullText[i:])
			break
		end = idx + len(findText)
		if not wholeWordsOnly or _isWordBoundary(fullText, idx, end):
			parts.append(fullText[i:idx])
			parts.append(_applyReplacementCase(fullText[idx:end], replaceText))
			count += 1
			i = end
		else:
			parts.append(fullText[i : idx + 1])
			i = idx + 1
	return "".join(parts), count


class ClipboardEditorDialog(wx.Dialog):
	def __init__(
		self,
		parent,
		initialText,
		onClose,
		onSave=None,
	):
		super().__init__(
			parent,
			title=_("Clipboard Content Editor"),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)
		self._onClose = onClose
		self._onSave = onSave
		self._initialText = initialText
		self._resultMessage = None
		self._resultKind = None
		self._closing = False
		self._findDialog = None
		self._findOnlyDialog = None

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		textLabel = wx.StaticText(self, label=_("Clipboard content:"))
		mainSizer.Add(textLabel, flag=wx.ALL | wx.EXPAND, border=8)

		textSizer = wx.BoxSizer(wx.HORIZONTAL)
		self._textCtrl = wx.TextCtrl(
			self,
			value=initialText,
			style=wx.TE_MULTILINE | wx.TE_RICH2,
		)
		textSizer.Add(self._textCtrl, proportion=1, flag=wx.EXPAND)
		mainSizer.Add(textSizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=8)

		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self._toolsMenuId = wx.NewIdRef()
		self._toolsButton = wx.Button(self, id=self._toolsMenuId, label=_("&Tools"))
		buttonSizer.Add(self._toolsButton, flag=wx.RIGHT, border=5)

		self._saveButton = wx.Button(self, wx.ID_SAVE, label=_("Save (Ctrl+S)"))
		self._saveAsId = wx.NewIdRef()
		self._saveAsButton = wx.Button(self, self._saveAsId, label=_("Save As... (Ctrl+Shift+S)"))
		self._cancelButton = wx.Button(self, wx.ID_CANCEL, label=_("Cancel (Esc)"))
		self._saveButton.SetDefault()
		buttonSizer.Add(self._saveButton, flag=wx.RIGHT, border=5)
		buttonSizer.Add(self._saveAsButton, flag=wx.RIGHT, border=5)
		buttonSizer.Add(self._cancelButton)
		mainSizer.Add(buttonSizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=8)

		self.SetSizer(mainSizer)
		self.SetMinSize((420, 300))
		self.Layout()

		self._saveButton.Bind(wx.EVT_BUTTON, self.onSave)
		self._saveAsButton.Bind(wx.EVT_BUTTON, self.onSaveAs)
		self._cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
		self._toolsButton.Bind(wx.EVT_BUTTON, self.onToolsMenu)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Bind(wx.EVT_MENU, self.onSave, id=wx.ID_SAVE)
		self.Bind(wx.EVT_MENU, self.onSaveAs, id=self._saveAsId)
		self.Bind(wx.EVT_MENU, self.onCancel, id=wx.ID_CANCEL)

		accels = [
			(wx.ACCEL_CTRL, ord("S"), wx.ID_SAVE),
			(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("S"), self._saveAsId),
			(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL),
		]
		self.SetAcceleratorTable(wx.AcceleratorTable(accels))

	def onSave(self, evt):
		text = self._textCtrl.GetValue()
		if self._onSave:
			self._onSave(self._initialText)
		try:
			if _copyTextToClipboard(text):
				self._resultMessage = _("Clipboard updated")
				self._resultKind = "saved"
			else:
				self._resultMessage = _("Failed to update clipboard")
				self._resultKind = "failed"
		except Exception:
			self._resultMessage = _("Failed to update clipboard")
			self._resultKind = "failed"
		self._announceAndClose()

	def onSaveAs(self, evt):
		_playSound(500, 50)
		text = self._textCtrl.GetValue()
		with wx.FileDialog(
			self,
			_("Save as"),
			wildcard=_("Text files (*.txt)|*.txt|All files (*.*)|*.*"),
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
		) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return
			path = fileDialog.GetPath()
			try:
				with open(path, "w", encoding="utf-8") as f:
					f.write(text)
				self._resultMessage = _("File saved")
				self._resultKind = "saved"
				wx.CallAfter(self._announceAndClose)
			except Exception as e:
				self._resultMessage = _("Error saving file: {error}").format(error=str(e))
				self._resultKind = "failed"
				wx.CallAfter(self._announceAndClose)

	def onToolsMenu(self, evt):
		menu = wx.Menu()
		idSpeech = wx.NewIdRef()
		idInfo = wx.NewIdRef()
		idFind = wx.NewIdRef()
		idReplace = wx.NewIdRef()
		idUpper = wx.NewIdRef()
		idLower = wx.NewIdRef()
		idTitle = wx.NewIdRef()
		idTrim = wx.NewIdRef()
		idRemoveEmpty = wx.NewIdRef()
		idStripHtml = wx.NewIdRef()

		menu.Append(idSpeech, _("&Speech"))
		menu.Append(idInfo, _("&Information"))
		menu.Append(idFind, _("&Find"))
		menu.Append(idReplace, _("&Replace"))
		menu.AppendSeparator()
		menu.Append(idUpper, _("Convert to &uppercase"))
		menu.Append(idLower, _("Convert to &lowercase"))
		menu.Append(idTitle, _("Convert to &title case"))
		menu.AppendSeparator()
		menu.Append(idTrim, _("Trim &whitespace"))
		menu.Append(idRemoveEmpty, _("Remove &empty lines"))
		menu.Append(idStripHtml, _("Strip &HTML/Formatting"))

		self.Bind(wx.EVT_MENU, lambda e: wx.CallLater(100, ui.message, self._textCtrl.GetValue()), id=idSpeech)
		self.Bind(wx.EVT_MENU, self.onInformation, id=idInfo)
		self.Bind(wx.EVT_MENU, self.onFindDialog, id=idFind)
		self.Bind(wx.EVT_MENU, self.onReplaceDialog, id=idReplace)
		self.Bind(wx.EVT_MENU, lambda e: self._applyTextChange("upper"), id=idUpper)
		self.Bind(wx.EVT_MENU, lambda e: self._applyTextChange("lower"), id=idLower)
		self.Bind(wx.EVT_MENU, lambda e: self._applyTextChange("title"), id=idTitle)
		self.Bind(wx.EVT_MENU, lambda e: self._applyTextChange("trim"), id=idTrim)
		self.Bind(wx.EVT_MENU, lambda e: self._applyTextChange("remove_empty"), id=idRemoveEmpty)
		self.Bind(wx.EVT_MENU, lambda e: self._applyTextChange("strip_html"), id=idStripHtml)

		self._toolsButton.PopupMenu(menu)
		menu.Destroy()

	def _applyTextChange(self, action):
		selStart, selEnd = self._textCtrl.GetSelection()
		text = self._textCtrl.GetValue()
		hasSelection = selStart != selEnd

		if hasSelection:
			targetText = text[selStart:selEnd]
		else:
			targetText = text

		if action == "upper":
			newText = targetText.upper()
		elif action == "lower":
			newText = targetText.lower()
		elif action == "title":
			newText = targetText.title()
		elif action == "trim":
			newText = "\n".join([line.strip() for line in targetText.splitlines()])
		elif action == "remove_empty":
			newText = "\n".join([line for line in targetText.splitlines() if line.strip()])
		elif action == "strip_html":
			import re
			newText = re.sub(r'<[^>]+>', '', targetText)
		else:
			return

		if newText != targetText:
			if hasSelection:
				self._textCtrl.Replace(selStart, selEnd, newText)
				self._textCtrl.SetSelection(selStart, selStart + len(newText))
			else:
				self._textCtrl.SetValue(newText)
			_playSound(500, 50)

	def onCancel(self, evt):
		if self._textCtrl.GetValue() == self._initialText:
			self._resultMessage = None
			self._resultKind = "canceled"
			self._announceAndClose()
			return
		if not self._confirmDiscard():
			return
		self._resultMessage = _("Changes canceled")
		self._resultKind = "canceled"
		self._announceAndClose()

	def onClose(self, evt):
		if self._textCtrl.GetValue() == self._initialText:
			self._resultMessage = None
			self._resultKind = "canceled"
			self._announceAndClose()
			return
		if not self._confirmDiscard():
			return
		if not self._resultMessage:
			self._resultMessage = _("Changes canceled")
			self._resultKind = "canceled"
		self._announceAndClose()

	def onFindDialog(self, evt):
		_playSound(500, 50)
		self._showFind(focusEdit=True)

	def onInformation(self, evt):
		text = self._textCtrl.GetValue()
		if not text:
			wx.CallLater(100, _announceClipboardEmpty)
			return
		_playSound(660, 60)
		wx.CallLater(100, ui.message, _buildInformationMessage(text))

	def onReplaceDialog(self, evt):
		_playSound(500, 50)
		self._showFindReplace(focusReplace=False)

	def _showFind(self, focusEdit):
		if not self._findOnlyDialog:
			self._findOnlyDialog = FindDialog(self, self._textCtrl)
		self._findOnlyDialog.Show()
		self._findOnlyDialog.Raise()
		if focusEdit:
			self._findOnlyDialog.focusFind()

	def _showFindReplace(self, focusReplace):
		if not self._findDialog:
			self._findDialog = FindReplaceDialog(self, self._textCtrl)
		self._findDialog.Show()
		self._findDialog.Raise()
		self._findDialog.focusReplace(focusReplace)

	def _finalizeClose(self):
		if self._findDialog:
			try:
				self._findDialog.Destroy()
			except Exception:
				pass
			self._findDialog = None
		if self._findOnlyDialog:
			try:
				self._findOnlyDialog.Destroy()
			except Exception:
				pass
			self._findOnlyDialog = None
		if self._onClose:
			self._onClose()
		super().Destroy()

	def _announceAndClose(self):
		if self._closing:
			return
		self._closing = True
		
		# Play sound based on result kind
		if self._resultKind == "saved":
			_playSound(880, 70)
			icon = wx.ICON_INFORMATION
		elif self._resultKind == "canceled":
			_playSound(440, 70)
			icon = wx.ICON_INFORMATION
		else: # failed or others
			_playSound(330, 100)
			icon = wx.ICON_ERROR

		if self._resultMessage:
			gui.messageBox(
				self._resultMessage,
				_("Clipboard Content Editor"),
				wx.OK | icon,
				parent=self,
			)
		self._finalizeClose()

	def _confirmDiscard(self):
		if self._textCtrl.GetValue() == self._initialText:
			return True
		result = gui.messageBox(
			_("You have unsaved changes. Discard them?"),
			_("Clipboard Content Editor"),
			wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
			parent=self,
		)
		return result == wx.YES


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = ADDON_SUMMARY

	def __init__(self):
		super().__init__()
		self._editorDialog = None
		self._historyDialog = None
		self._backupHistory = []
		self._clipboardHistory = []
		self._appendModeEnabled = False
		self._lastClipboardText = None
		self._evtHandler = wx.EvtHandler()
		self._clipTimer = wx.Timer(self._evtHandler)
		self._evtHandler.Bind(wx.EVT_TIMER, self._onClipTimer, self._clipTimer)
		self._clipTimer.Start(1000)
		NVDASettingsDialog.categoryClasses.append(AddonSettingsPanel)

		self.switch = False
		self.commandLayerGestures = {
			"kb:e": "openEditor",
			"kb:r": "restorePrevious",
			"kb:i": "informationClipboard",
			"kb:s": "speakClipboard",
			"kb:h": "showHistory",
			"kb:a": "toggleAppendMode",
			"kb:f1": "showHelp",
			"kb:escape": "exitLayer",
		}

	def terminate(self):
		self._clipTimer.Stop()
		if self._editorDialog:
			try:
				self._editorDialog.Destroy()
			except Exception:
				pass
			self._editorDialog = None
		if self._historyDialog:
			try:
				self._historyDialog.Destroy()
			except Exception:
				pass
			self._historyDialog = None
		NVDASettingsDialog.categoryClasses.remove(AddonSettingsPanel)
		super().terminate()

	def _onClipTimer(self, evt=None):
		try:
			currentText = api.getClipData()
		except Exception:
			return
		
		if not currentText:
			return

		if self._lastClipboardText is None:
			self._lastClipboardText = currentText
			if currentText not in self._clipboardHistory:
				self._clipboardHistory.insert(0, currentText)
			return

		if currentText != self._lastClipboardText:
			if self._appendModeEnabled:
				combined = self._lastClipboardText + "\r\n" + currentText
				try:
					if _copyTextToClipboard(combined):
						self._lastClipboardText = combined
						ui.message(_("Appended"))
						if combined not in self._clipboardHistory:
							self._clipboardHistory.insert(0, combined)
				except Exception:
					pass
			else:
				self._lastClipboardText = currentText
				if currentText in self._clipboardHistory:
					self._clipboardHistory.remove(currentText)
				self._clipboardHistory.insert(0, currentText)
				
				# Limit history size
				size_limit_str = config.conf["ClipboardContentEditor"].get("historySize", "10")
				if size_limit_str.lower() != "all":
					try:
						limit = int(size_limit_str)
						if len(self._clipboardHistory) > limit:
							self._clipboardHistory = self._clipboardHistory[:limit]
					except ValueError:
						pass

	def _backupClipboard(self, previousText):
		if not config.conf["ClipboardContentEditor"].get("protectModeEnabled", True):
			return
		if previousText is None:
			return
		self._backupHistory.insert(0, previousText)
		maxLevels = max(1, int(config.conf["ClipboardContentEditor"].get("backupLevels", 1)))
		self._backupHistory = self._backupHistory[:maxLevels]

	def _openEditor(self):
		if self._editorDialog and self._editorDialog.IsShown():
			self._editorDialog.Raise()
			return
		try:
			text = api.getClipData()
		except Exception:
			text = ""
		self._editorDialog = ClipboardEditorDialog(
			gui.mainFrame,
			text,
			onClose=self._onEditorClosed,
			onSave=self._backupClipboard,
		)
		self._editorDialog.Show()
		self._editorDialog.Raise()
		self._editorDialog._textCtrl.SetFocus()
		_playSound(550, 60)

	def _onEditorClosed(self):
		self._editorDialog = None

	def getScript(self, gesture):
		if self.switch:
			script_name = None
			for identifier in gesture.identifiers:
				if identifier in self.commandLayerGestures:
					script_name = "script_" + self.commandLayerGestures[identifier]
					break
			
			if script_name:
				target_script = getattr(self, script_name)
				should_speak = (script_name == "script_exitLayer")
				
				def _wrapped_script(gesture, _speak=should_speak, _target=target_script):
					self.closeCommandsLayer(speak=_speak)
					if not _speak:
						wx.CallLater(50, _target, gesture)
					else:
						_target(gesture)
				return _wrapped_script
			else:
				self.closeCommandsLayer(speak=True)

		return super().getScript(gesture)

	def closeCommandsLayer(self, speak=True):
		if self.switch:
			_playSound(400, 100)
		if speak:
			ui.message(_("Exited Clipboard Content Editor command layer"))
		self.switch = False

	@script(
		description=_("Activates Clipboard Content Editor command layer"),
		gesture="kb:control+alt+c"
	)
	def script_activateCommandLayer(self, gesture):
		_playSound(800, 100)
		ui.message(_("Enter Clipboard Content Editor command layer. Press F1 for help."))
		self.switch = True

	def script_exitLayer(self, gesture):
		pass

	def script_openEditor(self, gesture):
		wx.CallAfter(self._openEditor)

	def _getClipboardText(self):
		try:
			return api.getClipData() or ""
		except Exception:
			return ""

	def _informationClipboard(self):
		text = self._getClipboardText()
		if not text:
			_announceClipboardEmpty()
			return
		_playSound(660, 60)
		ui.message(_buildInformationMessage(text))

	def script_informationClipboard(self, gesture):
		if self._editorDialog and self._editorDialog.IsShown() and self._editorDialog.IsActive():
			self._editorDialog.onInformation(gesture)
			return
		self._informationClipboard()

	def script_restorePrevious(self, gesture):
		if not config.conf["ClipboardContentEditor"].get("protectModeEnabled", True):
			ui.message(_("Protect mode is disabled"))
			return
		if not self._backupHistory:
			_playSound(330, 100)
			ui.message(_("No backup available"))
			return
		previousText = self._backupHistory.pop(0)
		if api.copyToClip(previousText):
			self._lastClipboardText = previousText
			_playSound(880, 70)
			ui.message(_("Previous clipboard restored"))
		else:
			_playSound(330, 100)
			ui.message(_("Failed to restore clipboard"))

	def script_speakClipboard(self, gesture):
		text = self._getClipboardText()
		if not text:
			_announceClipboardEmpty()
			return
		ui.message(text)

	def script_toggleAppendMode(self, gesture):
		self._appendModeEnabled = not self._appendModeEnabled
		if self._appendModeEnabled:
			ui.message(_("Append mode on"))
		else:
			ui.message(_("Append mode off"))

	def _openHistoryDialog(self):
		if self._historyDialog and self._historyDialog.IsShown():
			self._historyDialog.Raise()
			return
		self._historyDialog = ClipboardHistoryDialog(gui.mainFrame, self._clipboardHistory, self)
		self._historyDialog.Show()
		self._historyDialog.Raise()
		_playSound(550, 60)

	def script_showHistory(self, gesture):
		wx.CallAfter(self._openHistoryDialog)

	def script_showHelp(self, gesture):
		def _show():
			gui.mainFrame.prePopup()
			try:
				choices = [_("Command List"), _("Full Documentation")]
				dlg = wx.SingleChoiceDialog(gui.mainFrame, _(" "), _("What do you want to show?"), choices)
				dlg.SetSelection(0)
				res = dlg.ShowModal()
				sel = dlg.GetSelection()
				dlg.Destroy()
			finally:
				gui.mainFrame.postPopup()
			
			if res == wx.ID_OK:
				if sel == 0:
					msg = _("Clipboard Content Editor Command List\n--------------------\nF1: Open Command List or Full Documentation\nA: On / Off Append Mode\nE: Open Clipboard Editor\nR: Restore Editor Backup\nI: Say Clipboard Information\nS: Speak Clipboard Content\nH: Open Clipboard History Manager")
					
					gui.mainFrame.prePopup()
					try:
						info_dlg = InfoDialog(gui.mainFrame, _("Clipboard Content Editor Command List"), msg)
						info_dlg.ShowModal()
						info_dlg.Destroy()
					finally:
						gui.mainFrame.postPopup()
				elif sel == 1:
					import os
					import languageHandler
					
					lang = config.conf["ClipboardContentEditor"].get("language", "default")
					if lang == "default":
						lang = languageHandler.getLanguage()[:2]
					
					addon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
					html_path = os.path.join(addon_dir, "doc", lang, "readme.html")
					if not os.path.exists(html_path):
						html_path = os.path.join(addon_dir, "doc", "id", "readme.html")
					if not os.path.exists(html_path):
						html_path = os.path.join(addon_dir, "doc", "en", "readme.html")
					
					if os.path.exists(html_path):
						try:
							with open(html_path, "r", encoding="utf-8") as f:
								html_content = f.read()
							ui.browseableMessage(html_content, _("Clipboard Content Editor Documentation"), isHtml=True)
						except Exception as e:
							ui.message(f"Failed to load document: {e}")
					else:
						ui.message(_("Document is not available."))
		wx.CallAfter(_show)


class FindReplaceDialog(wx.Dialog):
	def __init__(self, parent, textCtrl):
		super().__init__(
			parent,
			title=_("Replace"),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)
		self._textCtrl = textCtrl

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, sizer=mainSizer)
		self.findEdit = sHelper.addLabeledControl(_("Source text"), wx.TextCtrl)
		self.replaceEdit = sHelper.addLabeledControl(_("Replacement text"), wx.TextCtrl)
		self.matchCaseCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("Case sensitive")))
		self.matchWholeWordsCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Replace whole words only, not part of other words")),
		)
		self.matchWholeWordsCheckBox.SetValue(True)

		buttonSizer = wx.StdDialogButtonSizer()
		self.findNextButton = wx.Button(self, label=_("Find next"))
		self.replaceButton = wx.Button(self, label=_("Replace"))
		self.replaceAllButton = wx.Button(self, label=_("Replace all"))
		self.closeButton = wx.Button(self, wx.ID_CLOSE)
		buttonSizer.AddButton(self.findNextButton)
		buttonSizer.AddButton(self.replaceButton)
		buttonSizer.AddButton(self.replaceAllButton)
		buttonSizer.AddButton(self.closeButton)
		buttonSizer.Realize()
		mainSizer.Add(buttonSizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=8)

		self.SetSizer(mainSizer)
		self.Layout()

		self.findNextButton.Bind(wx.EVT_BUTTON, self.onFindNext)
		self.replaceButton.Bind(wx.EVT_BUTTON, self.onReplace)
		self.replaceAllButton.Bind(wx.EVT_BUTTON, self.onReplaceAll)
		self.closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)

	def onCharHook(self, evt):
		if evt.GetKeyCode() == wx.WXK_ESCAPE:
			self.onClose(evt)
			return
		evt.Skip()

	def focusReplace(self, focusReplace):
		if focusReplace:
			self.replaceEdit.SetFocus()
		else:
			self.findEdit.SetFocus()

	def onFindNext(self, evt):
		findText = self.findEdit.GetValue()
		if not findText:
			ui.message(_("Find text is empty"))
			return False
		matchCase = self.matchCaseCheckBox.GetValue()
		wholeWordsOnly = self.matchWholeWordsCheckBox.GetValue()
		fullText = self._textCtrl.GetValue()
		start, end = self._textCtrl.GetSelection()
		found = _findNext(fullText, findText, end, matchCase, wholeWordsOnly)
		if found is None:
			found = _findNext(fullText, findText, 0, matchCase, wholeWordsOnly)
		if found is None:
			_playSound(330, 100)
			ui.message(_("Text not found"))
			return False
		self._textCtrl.SetFocus()
		self._textCtrl.SetSelection(found[0], found[1])
		_playSound(750, 40)
		return True

	def onReplace(self, evt):
		findText = self.findEdit.GetValue()
		if not findText:
			ui.message(_("Find text is empty"))
			return
		replaceText = self.replaceEdit.GetValue()
		matchCase = self.matchCaseCheckBox.GetValue()
		wholeWordsOnly = self.matchWholeWordsCheckBox.GetValue()
		fullText = self._textCtrl.GetValue()
		start, end = self._textCtrl.GetSelection()
		selected = self._textCtrl.GetStringSelection()
		replaced = False
		if (
			_selectionMatches(
				fullText,
				start,
				end,
				selected,
				findText,
				matchCase,
				wholeWordsOnly,
			)
			and start != end
		):
			replacement = _applyReplacementCase(selected, replaceText)
			self._textCtrl.Replace(start, end, replacement)
			self._textCtrl.SetSelection(start, start + len(replacement))
			replaced = True
			_playSound(750, 40)
		if not replaced:
			self.onFindNext(evt)
			start, end = self._textCtrl.GetSelection()
			selected = self._textCtrl.GetStringSelection()
			fullText = self._textCtrl.GetValue()
			if (
				_selectionMatches(
					fullText,
					start,
					end,
					selected,
					findText,
					matchCase,
					wholeWordsOnly,
				)
				and start != end
			):
				replacement = _applyReplacementCase(selected, replaceText)
				self._textCtrl.Replace(start, end, replacement)
				self._textCtrl.SetSelection(start, start + len(replacement))
				replaced = True
				_playSound(750, 40)
		if replaced:
			self._resetAndHide()

	def onReplaceAll(self, evt):
		findText = self.findEdit.GetValue()
		if not findText:
			ui.message(_("Find text is empty"))
			return
		replaceText = self.replaceEdit.GetValue()
		matchCase = self.matchCaseCheckBox.GetValue()
		wholeWordsOnly = self.matchWholeWordsCheckBox.GetValue()
		fullText = self._textCtrl.GetValue()
		newText, count = _replaceAll(
			fullText,
			findText,
			replaceText,
			matchCase,
			wholeWordsOnly,
		)
		if count == 0:
			_playSound(330, 100)
			ui.message(_("Text not found"))
			return
		self._textCtrl.SetValue(newText)
		_playSound(880, 70)
		ui.message(_("{count} replacements").format(count=count))
		self._resetAndHide()

	def onClose(self, evt):
		_playSound(440, 70)
		self.Hide()

	def _resetAndHide(self):
		self.findEdit.SetValue("")
		self.replaceEdit.SetValue("")
		self.Hide()


class FindDialog(wx.Dialog):
	def __init__(self, parent, textCtrl):
		super().__init__(
			parent,
			title=_("Find"),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)
		self._textCtrl = textCtrl

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, sizer=mainSizer)
		self.findEdit = sHelper.addLabeledControl(_("Find what"), wx.TextCtrl)
		self.matchCaseCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("Case sensitive")))
		self.matchWholeWordsCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Find whole words only, not part of other words")),
		)
		self.matchWholeWordsCheckBox.SetValue(True)

		buttonSizer = wx.StdDialogButtonSizer()
		self.findNextButton = wx.Button(self, label=_("Find next"))
		self.closeButton = wx.Button(self, wx.ID_CLOSE)
		buttonSizer.AddButton(self.findNextButton)
		buttonSizer.AddButton(self.closeButton)
		buttonSizer.Realize()
		mainSizer.Add(buttonSizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=8)

		self.SetSizer(mainSizer)
		self.Layout()

		self.findNextButton.Bind(wx.EVT_BUTTON, self.onFindNext)
		self.closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)

	def onCharHook(self, evt):
		if evt.GetKeyCode() == wx.WXK_ESCAPE:
			self.onClose(evt)
			return
		if evt.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			self.onFindNext(evt)
			return
		evt.Skip()

	def focusFind(self):
		self.findEdit.SetFocus()

	def onFindNext(self, evt):
		findText = self.findEdit.GetValue()
		if not findText:
			ui.message(_("Find text is empty"))
			return
		matchCase = self.matchCaseCheckBox.GetValue()
		wholeWordsOnly = self.matchWholeWordsCheckBox.GetValue()
		fullText = self._textCtrl.GetValue()
		start, end = self._textCtrl.GetSelection()
		found = _findNext(fullText, findText, end, matchCase, wholeWordsOnly)
		if found is None:
			found = _findNext(fullText, findText, 0, matchCase, wholeWordsOnly)
		if found is None:
			_playSound(330, 100)
			ui.message(_("Text not found"))
			return
		self._textCtrl.SetFocus()
		self._textCtrl.SetSelection(found[0], found[1])
		_playSound(750, 40)



	def onClose(self, evt):
		_playSound(440, 70)
		self.Hide()


class ClipboardHistoryDialog(wx.Dialog):
	def __init__(self, parent, history, plugin_ref):
		super().__init__(
			parent,
			title=_("Clipboard History"),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
		)
		self.history = history
		self.plugin = plugin_ref
		self.Bind(wx.EVT_CLOSE, self.onCloseDialog)
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		
		label = wx.StaticText(self, label=_("Recent clipboard items:"))
		mainSizer.Add(label, flag=wx.ALL, border=8)
		
		# Replace newlines with spaces for single-line display in listbox
		display_choices = [(item[:80] + "..." if len(item)>80 else item).replace('\r\n', ' ').replace('\n', ' ') for item in history]
		self.listBox = wx.ListBox(self, choices=display_choices)
		mainSizer.Add(self.listBox, proportion=1, flag=wx.ALL | wx.EXPAND, border=8)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btnOptions = wx.Button(self, label=_("&Action"))
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label=_("Close"))
		
		self.btnClose.SetDefault()
		
		btnSizer.Add(self.btnOptions, flag=wx.RIGHT, border=5)
		btnSizer.Add(self.btnClose)
		
		mainSizer.Add(btnSizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=8)
		self.SetSizer(mainSizer)
		self.SetMinSize((500, 350))
		
		self.btnOptions.Bind(wx.EVT_BUTTON, self.onOptionsBtn)
		self.btnClose.Bind(wx.EVT_BUTTON, self.onCloseDialog)
		self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)
		
		self.listBox.SetFocus()
		if self.history:
			self.listBox.SetSelection(0)
			
	def onOptionsBtn(self, evt):
		menu = wx.Menu()
		idRestore = wx.NewIdRef()
		idEdit = wx.NewIdRef()
		idDelete = wx.NewIdRef()
		idClear = wx.NewIdRef()
		
		menu.Append(idRestore, _("&Restore"))
		menu.Append(idEdit, _("&Edit"))
		menu.AppendSeparator()
		menu.Append(idDelete, _("&Delete"))
		menu.Append(idClear, _("&Clear All"))
		
		self.Bind(wx.EVT_MENU, self.onRestore, id=idRestore)
		self.Bind(wx.EVT_MENU, self.onEdit, id=idEdit)
		self.Bind(wx.EVT_MENU, self.onDelete, id=idDelete)
		self.Bind(wx.EVT_MENU, self.onClear, id=idClear)
		
		self.btnOptions.PopupMenu(menu)
		menu.Destroy()
			
	def onCharHook(self, evt):
		if evt.GetKeyCode() == wx.WXK_ESCAPE:
			self.onCloseDialog(evt)
			return
		if evt.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			self.onRestore(None)
			return
		evt.Skip()
		
	def onCloseDialog(self, evt):
		self.plugin._historyDialog = None
		self.Destroy()

	def onRestore(self, evt):
		idx = self.listBox.GetSelection()
		if idx != wx.NOT_FOUND:
			text = self.history[idx]
			if _copyTextToClipboard(text):
				self.plugin._lastClipboardText = text
				ui.message(_("Clipboard updated"))
				_playSound(880, 70)
			self.onCloseDialog(evt)

	def onEdit(self, evt):
		idx = self.listBox.GetSelection()
		if idx != wx.NOT_FOUND:
			text = self.history[idx]
			if _copyTextToClipboard(text):
				self.plugin._lastClipboardText = text
			self.onCloseDialog(evt)
			wx.CallAfter(self.plugin._openEditor)

	def onDelete(self, evt):
		idx = self.listBox.GetSelection()
		if idx != wx.NOT_FOUND:
			if gui.messageBox(
				_("Are you sure you want to delete this item?"),
				_("Confirm Deletion"),
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
				self
			) == wx.YES:
				del self.history[idx]
				self.listBox.Delete(idx)
				if self.history:
					self.listBox.SetSelection(min(idx, len(self.history)-1))
				else:
					self.listBox.SetFocus()

	def onClear(self, evt):
		if not self.history:
			return
		if gui.messageBox(
			_("Are you sure you want to clear the entire clipboard history?"),
			_("Confirm Clear All"),
			wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
			self
		) == wx.YES:
			self.history.clear()
			self.listBox.Clear()


class AddonSettingsPanel(SettingsPanel):
	title = ADDON_SUMMARY

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		
		self.languageChoices = ["default"]
		self.languageLabels = [_("Default (NVDA Language)")]
		
		try:
			import languageHandler
			import os
			locale_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "locale")
			if os.path.isdir(locale_dir):
				langs = [d for d in os.listdir(locale_dir) if os.path.isdir(os.path.join(locale_dir, d))]
				langs.sort()
				for lang in langs:
					self.languageChoices.append(lang)
					try:
						desc = languageHandler.getLanguageDescription(lang)
						self.languageLabels.append(f"{desc} ({lang})")
					except Exception:
						self.languageLabels.append(lang)
		except Exception:
			# Fallback
			self.languageChoices = ["default", "en", "id", "ar", "uk"]
			self.languageLabels = [_("Default (NVDA Language)"), "English", "Bahasa Indonesia", "العربية", "Українська"]
		
		langLabel = _("Addon Language (requires NVDA restart to fully apply)")
		self.languageCombo = sHelper.addLabeledControl(
			langLabel,
			wx.Choice,
			choices=self.languageLabels
		)
		
		current_lang = config.conf["ClipboardContentEditor"].get("language", "default")
		try:
			idx = self.languageChoices.index(current_lang)
			self.languageCombo.SetSelection(idx)
		except ValueError:
			self.languageCombo.SetSelection(0)
			
		self.soundCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("Enable &sound")))
		try:
			val = config.conf["ClipboardContentEditor"].get("soundEnabled", True)
			self.soundCheckBox.SetValue(val if isinstance(val, bool) else str(val).lower() == "true")
		except Exception:
			self.soundCheckBox.SetValue(True)
		
		self.protectModeCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &protect mode (clipboard backup)")),
		)
		try:
			val = config.conf["ClipboardContentEditor"].get("protectModeEnabled", True)
			self.protectModeCheckBox.SetValue(val if isinstance(val, bool) else str(val).lower() == "true")
		except Exception:
			self.protectModeCheckBox.SetValue(True)
		
		try:
			backup_val = int(config.conf["ClipboardContentEditor"].get("backupLevels", 1))
		except Exception:
			backup_val = 1
			
		backupLabel = _("Number of backup &levels")
		self.backupLevelsSpin = sHelper.addLabeledControl(
			backupLabel,
			gui.nvdaControls.SelectOnFocusSpinCtrl,
			min=1,
			max=20,
			initial=backup_val,
		)
		
		# History Size Combobox
		self.historyChoices = ["10", "25", "50", "100", "All"]
		self.historyLabels = [_("10 Items"), _("25 Items"), _("50 Items"), _("100 Items"), _("Unlimited")]
		
		historyLabel = _("Clipboard History Limit")
		self.historyCombo = sHelper.addLabeledControl(
			historyLabel,
			wx.Choice,
			choices=self.historyLabels
		)
		
		current_history = config.conf["ClipboardContentEditor"].get("historySize", "10")
		try:
			idx = self.historyChoices.index(str(current_history))
			self.historyCombo.SetSelection(idx)
		except ValueError:
			self.historyCombo.SetSelection(0)

	def onSave(self):
		config.conf["ClipboardContentEditor"]["protectModeEnabled"] = self.protectModeCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["soundEnabled"] = self.soundCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["backupLevels"] = int(self.backupLevelsSpin.GetValue())
		
		config.conf["ClipboardContentEditor"]["historySize"] = self.historyChoices[self.historyCombo.GetSelection()]
		
		selectedLanguage = self.languageChoices[self.languageCombo.GetSelection()]
		oldLanguage = config.conf["ClipboardContentEditor"].get("language", "default")
		if selectedLanguage != oldLanguage:
			config.conf["ClipboardContentEditor"]["language"] = selectedLanguage
			def prompt_restart():
				if gui.messageBox(
					_("Language changed. A restart of NVDA is required to fully apply the new language. Restart now?"),
					_("Restart Required"),
					wx.YES_NO | wx.ICON_QUESTION,
					gui.mainFrame
				) == wx.YES:
					import core
					core.restart()
			wx.CallAfter(prompt_restart)

