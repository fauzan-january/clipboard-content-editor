# Clipboard Content Editor: edit clipboard text before pasting
# Copyright (C) 2026 Fauzan January
# Released under GPL 2

import addonHandler
import api
import globalPluginHandler
import gui
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel, NVDASettingsDialog
import core
import config
import speech
import tones
import ui
import wx
from scriptHandler import script

addonHandler.initTranslation()

ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]

confspec = {
	"protectModeEnabled": "boolean(default=True)",
	"backupLevels": "integer(default=1)",
	"previewEnabled": "boolean(default=True)",
	"summaryButtonEnabled": "boolean(default=True)",
	"findReplaceButtonEnabled": "boolean(default=True)",
	"clearButtonEnabled": "boolean(default=True)",
	"shortcutsWhenHiddenEnabled": "boolean(default=True)",
}
config.conf.spec["ClipboardContentEditor"] = confspec


def _buildInformationMessage(text):
	charCount = len(text)
	wordCount = len(text.split())
	lineCount = len(text.splitlines()) if text else 0
	return _("Information: {chars} characters, {words} words, {lines} lines").format(
		chars=charCount,
		words=wordCount,
		lines=lineCount,
	)


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


class ClipboardEditorDialog(wx.Dialog):
	def __init__(
		self,
		parent,
		initialText,
		onClose,
		onSave=None,
		enablePreview=True,
		enableSummaryButton=True,
		enableFindReplaceButton=True,
		enableClearButton=True,
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
		self._enablePreview = enablePreview
		self._enableSummaryButton = enableSummaryButton
		self._enableFindReplaceButton = enableFindReplaceButton
		self._enableClearButton = enableClearButton
		self._shortcutsWhenHiddenEnabled = shortcutsWhenHiddenEnabled
		self._findDialog = None

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
		self._clearMenuId = wx.NewIdRef()
		if self._enableClearButton:
			self._clearButton = wx.Button(self, id=self._clearMenuId, label=_("&Clear"))
			textSizer.Add(self._clearButton, flag=wx.LEFT, border=8)
		mainSizer.Add(textSizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=8)

		buttonSizer = wx.StdDialogButtonSizer()
		self._readMenuId = wx.NewIdRef()
		self._informationMenuId = wx.NewIdRef()
		self._findMenuId = wx.NewIdRef()
		if self._enablePreview:
			self._readButton = wx.Button(self, id=self._readMenuId, label=_("&Read"))
			buttonSizer.AddButton(self._readButton)
		if self._enableSummaryButton:
			self._informationButton = wx.Button(
				self,
				id=self._informationMenuId,
				label=_("&Information"),
			)
			buttonSizer.AddButton(self._informationButton)
		if self._enableFindReplaceButton:
			self._findButton = wx.Button(self, id=self._findMenuId, label=_("&Find/Replace"))
			buttonSizer.AddButton(self._findButton)
		self._saveButton = wx.Button(self, wx.ID_SAVE, label=_("&Save"))
		self._cancelButton = wx.Button(self, wx.ID_CANCEL, label=_("Cancel"))
		self._saveButton.SetDefault()
		buttonSizer.AddButton(self._saveButton)
		buttonSizer.AddButton(self._cancelButton)
		buttonSizer.Realize()
		mainSizer.Add(buttonSizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=8)

		self.SetSizer(mainSizer)
		self.SetMinSize((420, 300))
		self.Layout()

		self._saveButton.Bind(wx.EVT_BUTTON, self.onSave)
		self._cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
		if self._enableClearButton:
			self._clearButton.Bind(wx.EVT_BUTTON, self.onClear)
		if self._enablePreview:
			self._readButton.Bind(wx.EVT_BUTTON, self.onRead)
		if self._enableFindReplaceButton:
			self._findButton.Bind(wx.EVT_BUTTON, self.onFindReplace)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Bind(wx.EVT_MENU, self.onSave, id=wx.ID_SAVE)
		self.Bind(wx.EVT_MENU, self.onCancel, id=wx.ID_CANCEL)
		if self._enableClearButton or self._shortcutsWhenHiddenEnabled:
			self.Bind(wx.EVT_MENU, self.onClear, id=self._clearMenuId)
		if self._enablePreview or self._shortcutsWhenHiddenEnabled:
			self.Bind(wx.EVT_MENU, self.onRead, id=self._readMenuId)
		if self._enableFindReplaceButton or self._shortcutsWhenHiddenEnabled:
			self.Bind(wx.EVT_MENU, self.onFindReplace, id=self._findMenuId)
		if self._enableSummaryButton or self._shortcutsWhenHiddenEnabled:
			self.Bind(wx.EVT_MENU, self.onInformation, id=self._informationMenuId)
		if self._enableSummaryButton:
			self._informationButton.Bind(wx.EVT_BUTTON, self.onInformation)

		accels = []
		if self._enableClearButton or self._shortcutsWhenHiddenEnabled:
			accels.append((wx.ACCEL_ALT, ord("C"), int(self._clearMenuId)))
		if self._enablePreview or self._shortcutsWhenHiddenEnabled:
			accels.append((wx.ACCEL_ALT, ord("R"), int(self._readMenuId)))
		if self._enableSummaryButton or self._shortcutsWhenHiddenEnabled:
			accels.append((wx.ACCEL_ALT, ord("I"), int(self._informationMenuId)))
		if self._enableFindReplaceButton or self._shortcutsWhenHiddenEnabled:
			accels.append((wx.ACCEL_ALT, ord("F"), int(self._findMenuId)))
		accels.extend(
			[
				(wx.ACCEL_ALT, ord("S"), wx.ID_SAVE),
				(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL),
			],
		)
		self.SetAcceleratorTable(wx.AcceleratorTable(accels))

	def onClear(self, evt):
		self._textCtrl.SetValue("")
		if not _copyTextToClipboard(""):
			ui.message(_("Failed to clear clipboard"))
			return
		ui.message(_("Clipboard cleared"))
		self._textCtrl.SetFocus()

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

	def onCancel(self, evt):
		if not self._confirmDiscard():
			return
		self._resultMessage = _("Changes canceled")
		self._resultKind = "canceled"
		self._announceAndClose()

	def onClose(self, evt):
		if not self._confirmDiscard():
			return
		if not self._resultMessage:
			self._resultMessage = _("Changes canceled")
			self._resultKind = "canceled"
		self._announceAndClose()

	def onRead(self, evt):
		selection = self._textCtrl.GetStringSelection()
		text = selection if selection else self._textCtrl.GetValue()
		if not text:
			_announceClipboardEmpty()
			return
		speech.cancelSpeech()
		speech.speakMessage(text)

	def onFindReplace(self, evt):
		self._showFindReplace(focusReplace=False)

	def onInformation(self, evt):
		text = self._textCtrl.GetValue()
		if not text:
			_announceClipboardEmpty()
			return
		ui.message(_buildInformationMessage(text))

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
		if self._onClose:
			self._onClose()
		super().Destroy()

	def _announceAndClose(self):
		if self._closing:
			return
		self._closing = True
		if self._resultMessage:
			speech.cancelSpeech()
			if self._resultKind == "saved":
				tones.beep(880, 70)
				icon = wx.ICON_INFORMATION
			elif self._resultKind == "canceled":
				tones.beep(440, 70)
				icon = wx.ICON_INFORMATION
			else:
				tones.beep(330, 100)
				icon = wx.ICON_ERROR
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
			enablePreview=config.conf["ClipboardContentEditor"]["previewEnabled"],
			enableSummaryButton=config.conf["ClipboardContentEditor"]["summaryButtonEnabled"],
			enableFindReplaceButton=config.conf["ClipboardContentEditor"][
				"findReplaceButtonEnabled"
			],
			enableClearButton=config.conf["ClipboardContentEditor"]["clearButtonEnabled"],
			shortcutsWhenHiddenEnabled=config.conf["ClipboardContentEditor"][
				"shortcutsWhenHiddenEnabled"
			],
		)
		self._editorDialog.Show()
		self._editorDialog.Raise()
		self._editorDialog._textCtrl.SetFocus()
		tones.beep(660, 60)

	def _onEditorClosed(self):
		self._editorDialog = None

	@script(
		description=_("Opens a clipboard editor to modify the current clipboard text."),
		gesture="kb:control+alt+c",
	)
	def script_openEditor(self, gesture):
		wx.CallAfter(self._openEditor)

	def _getClipboardText(self):
		try:
			return api.getClipData() or ""
		except Exception:
			return ""

	def _readClipboard(self):
		text = self._getClipboardText()
		if not text:
			_announceClipboardEmpty()
			return
		speech.cancelSpeech()
		speech.speakMessage(text)

	def _informationClipboard(self):
		text = self._getClipboardText()
		if not text:
			_announceClipboardEmpty()
			return
		ui.message(_buildInformationMessage(text))

	@script(
		description=_("Reads the current clipboard text."),
		gesture="kb:alt+r",
	)
	def script_readClipboard(self, gesture):
		if self._editorDialog and self._editorDialog.IsShown() and self._editorDialog.IsActive():
			self._editorDialog.onRead(gesture)
			return
		self._readClipboard()

	@script(
		description=_("Shows information about the current clipboard text."),
		gesture="kb:alt+i",
	)
	def script_informationClipboard(self, gesture):
		if self._editorDialog and self._editorDialog.IsShown() and self._editorDialog.IsActive():
			self._editorDialog.onInformation(gesture)
			return
		self._informationClipboard()

	@script(
		description=_("Restores the previous clipboard content from backup."),
		gesture="kb:control+shift+z",
	)
	def script_restorePrevious(self, gesture):
		if not config.conf["ClipboardContentEditor"]["protectModeEnabled"]:
			ui.message(_("Protect mode is disabled"))
			return
		if not self._backupHistory:
			ui.message(_("No backup available"))
			return
		previousText = self._backupHistory.pop(0)
		if api.copyToClip(previousText):
			ui.message(_("Previous clipboard restored"))
		else:
			ui.message(_("Failed to restore clipboard"))


class FindReplaceDialog(wx.Dialog):
	def __init__(self, parent, textCtrl):
		super().__init__(
			parent,
			title=_("Find/Replace"),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)
		self._textCtrl = textCtrl

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, sizer=mainSizer)
		self.findEdit = sHelper.addLabeledControl(_("Find"), wx.TextCtrl)
		self.replaceEdit = sHelper.addLabeledControl(_("Replace"), wx.TextCtrl)
		self.matchCaseCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("Match case")))

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
			self.Hide()
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
			return
		matchCase = self.matchCaseCheckBox.GetValue()
		fullText = self._textCtrl.GetValue()
		start, end = self._textCtrl.GetSelection()
		found = self._findNext(fullText, findText, end, matchCase)
		if found is None:
			found = self._findNext(fullText, findText, 0, matchCase)
		if found is None:
			ui.message(_("Text not found"))
			return
		self._textCtrl.SetFocus()
		self._textCtrl.SetSelection(found[0], found[1])

	def onReplace(self, evt):
		findText = self.findEdit.GetValue()
		if not findText:
			ui.message(_("Find text is empty"))
			return
		replaceText = self.replaceEdit.GetValue()
		matchCase = self.matchCaseCheckBox.GetValue()
		fullText = self._textCtrl.GetValue()
		start, end = self._textCtrl.GetSelection()
		selected = self._textCtrl.GetStringSelection()
		replaced = False
		if (
			self._selectionMatches(fullText, start, end, selected, findText, matchCase)
			and start != end
		):
			self._textCtrl.Replace(start, end, replaceText)
			self._textCtrl.SetSelection(start, start + len(replaceText))
			replaced = True
		if not replaced:
			self.onFindNext(evt)
			start, end = self._textCtrl.GetSelection()
			selected = self._textCtrl.GetStringSelection()
			fullText = self._textCtrl.GetValue()
			if (
				self._selectionMatches(fullText, start, end, selected, findText, matchCase)
				and start != end
			):
				self._textCtrl.Replace(start, end, replaceText)
				self._textCtrl.SetSelection(start, start + len(replaceText))
				replaced = True
		if replaced:
			self._resetAndHide()

	def onReplaceAll(self, evt):
		findText = self.findEdit.GetValue()
		if not findText:
			ui.message(_("Find text is empty"))
			return
		replaceText = self.replaceEdit.GetValue()
		matchCase = self.matchCaseCheckBox.GetValue()
		fullText = self._textCtrl.GetValue()
		newText, count = self._replaceAll(fullText, findText, replaceText, matchCase)
		if count == 0:
			ui.message(_("Text not found"))
			return
		self._textCtrl.SetValue(newText)
		ui.message(_("{count} replacements").format(count=count))
		self._resetAndHide()

	def onClose(self, evt):
		self.Hide()

	def _resetAndHide(self):
		self.findEdit.SetValue("")
		self.replaceEdit.SetValue("")
		self.Hide()

	def _findNext(self, fullText, findText, startIndex, matchCase):
		if matchCase:
			return self._findNextMatch(fullText, findText, startIndex)
		return self._findNextMatch(fullText, findText, startIndex, ignoreCase=True)

	def _matches(self, selection, findText, matchCase):
		if not matchCase:
			return selection.lower() == findText.lower()
		return selection == findText

	def _selectionMatches(self, fullText, start, end, selection, findText, matchCase):
		if not selection:
			return False
		if not self._matches(selection, findText, matchCase):
			return False
		return self._isWordBoundary(fullText, start, end)

	def _isWordChar(self, ch):
		return ch.isalnum() or ch == "_"

	def _isWordBoundary(self, fullText, start, end):
		if start > 0 and self._isWordChar(fullText[start - 1]):
			return False
		if end < len(fullText) and self._isWordChar(fullText[end]):
			return False
		return True

	def _findNextMatch(self, fullText, findText, startIndex, ignoreCase=False):
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
			if self._isWordBoundary(fullText, idx, end):
				return idx, end
			i = idx + 1

	def _replaceAll(self, fullText, findText, replaceText, matchCase):
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
			if self._isWordBoundary(fullText, idx, end):
				parts.append(fullText[i:idx])
				parts.append(replaceText)
				count += 1
				i = end
			else:
				parts.append(fullText[i : idx + 1])
				i = idx + 1
		return "".join(parts), count


class AddonSettingsPanel(SettingsPanel):
	title = ADDON_SUMMARY

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.shortcutsWhenHiddenCheckBox = sHelper.addItem(
			wx.CheckBox(
				self,
				label=_("Keep shortcuts active when buttons are hidden in editor"),
			),
		)
		self.shortcutsWhenHiddenCheckBox.SetValue(
			config.conf["ClipboardContentEditor"]["shortcutsWhenHiddenEnabled"],
		)
		self.clearCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &clear button in editor")),
		)
		self.clearCheckBox.SetValue(
			config.conf["ClipboardContentEditor"]["clearButtonEnabled"],
		)
		self.previewCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &read button in editor")),
		)
		self.previewCheckBox.SetValue(config.conf["ClipboardContentEditor"]["previewEnabled"])
		self.summaryCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &information button in editor")),
		)
		self.summaryCheckBox.SetValue(
			config.conf["ClipboardContentEditor"]["summaryButtonEnabled"],
		)
		self.findReplaceCheckBox = sHelper.addItem(
			wx.CheckBox(self, label=_("Enable &find/replace button in editor")),
		)
		self.findReplaceCheckBox.SetValue(
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
		config.conf["ClipboardContentEditor"]["previewEnabled"] = self.previewCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["summaryButtonEnabled"] = self.summaryCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["clearButtonEnabled"] = self.clearCheckBox.GetValue()
		config.conf["ClipboardContentEditor"][
			"shortcutsWhenHiddenEnabled"
		] = self.shortcutsWhenHiddenCheckBox.GetValue()
		config.conf["ClipboardContentEditor"][
			"findReplaceButtonEnabled"
		] = self.findReplaceCheckBox.GetValue()
		config.conf["ClipboardContentEditor"]["backupLevels"] = int(self.backupLevelsSpin.GetValue())

