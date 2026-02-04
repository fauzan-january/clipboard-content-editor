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

ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]

confspec = {
	"protectModeEnabled": "boolean(default=True)",
	"backupLevels": "integer(default=1)",
	"summaryButtonEnabled": "boolean(default=True)",
	"findButtonEnabled": "boolean(default=True)",
	"findReplaceButtonEnabled": "boolean(default=True)",
	"shortcutsWhenHiddenEnabled": "boolean(default=True)",
	"soundEnabled": "boolean(default=True)",
}
config.conf.spec["ClipboardContentEditor"] = confspec


def _buildInformationMessage(text):
	charCount = len(text)
	wordCount = len(text.split())
	lineCount = len(text.splitlines()) if text else 0
	return _("Clipboard information: {chars} characters, {words} words, {lines} lines").format(
		chars=charCount,
		words=wordCount,
		lines=lineCount,
	)


def _playSound(hz, duration):
	if config.conf["ClipboardContentEditor"]["soundEnabled"]:
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
		enableSummaryButton=True,
		enableFindButton=True,
		enableFindReplaceButton=True,
		shortcutsWhenHiddenEnabled=True,
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
		self._enableSummaryButton = enableSummaryButton
		self._enableFindButton = enableFindButton
		self._enableReplaceButton = enableFindReplaceButton
		self._shortcutsWhenHiddenEnabled = shortcutsWhenHiddenEnabled
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
		self._informationMenuId = wx.NewIdRef()
		self._findMenuId = wx.NewIdRef()
		self._replaceMenuId = wx.NewIdRef()
		if self._enableSummaryButton:
			self._informationButton = wx.Button(
				self,
				id=self._informationMenuId,
				label=_("&Information"),
			)
			buttonSizer.Add(self._informationButton, flag=wx.RIGHT, border=5)
		if self._enableFindButton:
			self._findButton = wx.Button(self, id=self._findMenuId, label=_("&Find"))
			buttonSizer.Add(self._findButton, flag=wx.RIGHT, border=5)
		if self._enableReplaceButton:
			self._replaceButton = wx.Button(self, id=self._replaceMenuId, label=_("&Replace"))
			buttonSizer.Add(self._replaceButton, flag=wx.RIGHT, border=5)
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
		if self._enableFindButton:
			self._findButton.Bind(wx.EVT_BUTTON, self.onFindDialog)
		if self._enableReplaceButton:
			self._replaceButton.Bind(wx.EVT_BUTTON, self.onReplaceDialog)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Bind(wx.EVT_MENU, self.onSave, id=wx.ID_SAVE)
		self.Bind(wx.EVT_MENU, self.onSaveAs, id=self._saveAsId)
		self.Bind(wx.EVT_MENU, self.onCancel, id=wx.ID_CANCEL)
		if self._enableFindButton or self._shortcutsWhenHiddenEnabled:
			self.Bind(wx.EVT_MENU, self.onFindDialog, id=self._findMenuId)
		if self._enableReplaceButton or self._shortcutsWhenHiddenEnabled:
			self.Bind(wx.EVT_MENU, self.onReplaceDialog, id=self._replaceMenuId)
		if self._enableSummaryButton or self._shortcutsWhenHiddenEnabled:
			self.Bind(wx.EVT_MENU, self.onInformation, id=self._informationMenuId)
		if self._enableSummaryButton:
			self._informationButton.Bind(wx.EVT_BUTTON, self.onInformation)

		accels = []
		if self._enableSummaryButton or self._shortcutsWhenHiddenEnabled:
			accels.append((wx.ACCEL_ALT, ord("I"), int(self._informationMenuId)))
		if self._enableFindButton or self._shortcutsWhenHiddenEnabled:
			accels.append((wx.ACCEL_ALT, ord("F"), int(self._findMenuId)))
		if self._enableReplaceButton or self._shortcutsWhenHiddenEnabled:
			accels.append((wx.ACCEL_ALT, ord("R"), int(self._replaceMenuId)))
		accels.extend(
			[
				(wx.ACCEL_CTRL, ord("S"), wx.ID_SAVE),
				(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("S"), self._saveAsId),
				(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL),
			],
		)
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
				self._announceAndClose()
			except Exception as e:
				self._resultMessage = _("Error saving file: {error}").format(error=str(e))
				self._resultKind = "failed"
				self._announceAndClose()

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
			_announceClipboardEmpty()
			return
		_playSound(660, 60)
		ui.message(_buildInformationMessage(text))

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
		self._backupHistory = []
		NVDASettingsDialog.categoryClasses.append(AddonSettingsPanel)

	def terminate(self):
		if self._editorDialog:
			try:
				self._editorDialog.Destroy()
			except Exception:
				pass
			self._editorDialog = None
		NVDASettingsDialog.categoryClasses.remove(AddonSettingsPanel)
		super().terminate()

	def _backupClipboard(self, previousText):
		if not config.conf["ClipboardContentEditor"]["protectModeEnabled"]:
			return
		if previousText is None:
			return
		self._backupHistory.insert(0, previousText)
		maxLevels = max(1, int(config.conf["ClipboardContentEditor"]["backupLevels"]))
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
			enableSummaryButton=config.conf["ClipboardContentEditor"]["summaryButtonEnabled"],
			enableFindButton=config.conf["ClipboardContentEditor"]["findButtonEnabled"],
			enableFindReplaceButton=config.conf["ClipboardContentEditor"][
				"findReplaceButtonEnabled"
			],
			shortcutsWhenHiddenEnabled=config.conf["ClipboardContentEditor"][
				"shortcutsWhenHiddenEnabled"
			],
		)
		self._editorDialog.Show()
		self._editorDialog.Raise()
		self._editorDialog._textCtrl.SetFocus()
		_playSound(550, 60)

	def _onEditorClosed(self):
		self._editorDialog = None

	@script(
		description=_("Opens a clipboard editor to modify the current clipboard text."),
		gesture="kb:nvda+e",
	)
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

	@script(
		description=_("Shows information about the current clipboard text."),
		gesture="kb:nvda+i",
	)
	def script_informationClipboard(self, gesture):
		if self._editorDialog and self._editorDialog.IsShown() and self._editorDialog.IsActive():
			self._editorDialog.onInformation(gesture)
			return
		self._informationClipboard()

	@script(
		description=_("Restores the previous clipboard content from backup."),
		gesture="kb:nvda+z",
	)
	def script_restorePrevious(self, gesture):
		if not config.conf["ClipboardContentEditor"]["protectModeEnabled"]:
			ui.message(_("Protect mode is disabled"))
			return
		if not self._backupHistory:
			_playSound(330, 100)
			ui.message(_("No backup available"))
			return
		previousText = self._backupHistory.pop(0)
		if api.copyToClip(previousText):
			_playSound(880, 70)
			ui.message(_("Previous clipboard restored"))
		else:
			_playSound(330, 100)
			ui.message(_("Failed to restore clipboard"))


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


class AddonSettingsPanel(SettingsPanel):
	title = ADDON_SUMMARY

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.soundCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("Enable &sound")))
		self.soundCheckBox.SetValue(config.conf["ClipboardContentEditor"]["soundEnabled"])
		self.shortcutsWhenHiddenCheckBox = sHelper.addItem(
			wx.CheckBox(
				self,
				label=_("Keep shortcuts active when buttons are hidden in editor"),
			),
		)
		self.shortcutsWhenHiddenCheckBox.SetValue(
			config.conf["ClipboardContentEditor"]["shortcutsWhenHiddenEnabled"],
		)
		self.summaryCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &information button in editor")),
		)
		self.summaryCheckBox.SetValue(
			config.conf["ClipboardContentEditor"]["summaryButtonEnabled"],
		)
		self.findCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &find button in editor")),
		)
		self.findCheckBox.SetValue(config.conf["ClipboardContentEditor"]["findButtonEnabled"])
		self.replaceCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &replace button in editor")),
		)
		self.replaceCheckBox.SetValue(
			config.conf["ClipboardContentEditor"]["findReplaceButtonEnabled"],
		)
		self.protectModeCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &protect mode (clipboard backup)")),
		)
		self.protectModeCheckBox.SetValue(config.conf["ClipboardContentEditor"]["protectModeEnabled"])
		backupLabel = _("Number of backup &levels")
		self.backupLevelsSpin = sHelper.addLabeledControl(
			backupLabel,
			gui.nvdaControls.SelectOnFocusSpinCtrl,
			min=1,
			max=20,
			initial=int(config.conf["ClipboardContentEditor"]["backupLevels"]),
		)

	def onSave(self):
		config.conf["ClipboardContentEditor"]["protectModeEnabled"] = self.protectModeCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["summaryButtonEnabled"] = self.summaryCheckBox.GetValue()
		config.conf["ClipboardContentEditor"][
			"shortcutsWhenHiddenEnabled"
		] = self.shortcutsWhenHiddenCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["soundEnabled"] = self.soundCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["findButtonEnabled"] = self.findCheckBox.GetValue()
		config.conf["ClipboardContentEditor"][
			"findReplaceButtonEnabled"
		] = self.replaceCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["backupLevels"] = int(self.backupLevelsSpin.GetValue())

