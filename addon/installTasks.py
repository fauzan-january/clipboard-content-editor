# -*- coding: utf-8 -*-

# Clipboard Content Editor: edit clipboard text before pasting
# Copyright (C) 2026 Fauzan January
# Released under GPL 2

# Install Tasks for Clipboard Content Editor Add-on

import addonHandler
import gui
import os
import threading
import wx

try:
	import languageHandler
except ImportError:
	languageHandler = None

addonHandler.initTranslation()

WHATS_NEW_FILENAME = "whats-new.txt"


def _get_whats_new_path():
	addon_dir = os.path.dirname(__file__)
	candidates = []
	if languageHandler:
		lang = languageHandler.getLanguage()
		if lang:
			candidates.append(
				os.path.join(addon_dir, "locale", lang, WHATS_NEW_FILENAME)
			)
			if "_" in lang:
				candidates.append(
					os.path.join(
						addon_dir,
						"locale",
						lang.split("_", 1)[0],
						WHATS_NEW_FILENAME,
					)
				)
	candidates.append(os.path.join(addon_dir, WHATS_NEW_FILENAME))
	for path in candidates:
		if os.path.isfile(path):
			return path
	return None


def _load_whats_new_text():
	path = _get_whats_new_path()
	if not path:
		return _("What's new information is unavailable.")
	try:
		with open(path, "r", encoding="utf-8") as handle:
			text = handle.read().strip()
	except Exception:
		return _("What's new information is unavailable.")
	if not text:
		return _("What's new information is unavailable.")
	return text


class WhatsNewDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title=_("Clipboard Content Editor - What's New"))
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		whats_new_text = _load_whats_new_text()
		info_text = wx.TextCtrl(
			self,
			value=whats_new_text,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN,
			size=(520, 180),
		)
		info_text.SetFocus()
		main_sizer.Add(info_text, 1, wx.ALL | wx.EXPAND, 15)

		ok_btn = wx.Button(self, wx.ID_OK, label=_("&OK"))
		ok_btn.SetDefault()
		main_sizer.Add(ok_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		self.SetSizerAndFit(main_sizer)
		self.Bind(wx.EVT_CLOSE, self._on_close)

	def _on_close(self, evt):
		self.EndModal(wx.ID_OK)


class InstallPromptDialog(wx.Dialog):
	def _on_close(self, evt):
		self.EndModal(wx.ID_OK)

	def _on_view_whats_new(self, evt):
		self.EndModal(wx.ID_MORE)

	def __init__(self, parent):
		super().__init__(parent, title=_("Clipboard Content Editor - Installation"))
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		message = _(
			"Do you want to continue installation or see what's new first?"
		)
		text = wx.StaticText(self, label=message)
		text.Wrap(480)
		main_sizer.Add(text, 0, wx.ALL, 15)

		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		view_new_btn = wx.Button(self, label=_("&See what's new"))
		continue_btn = wx.Button(
			self, wx.ID_OK, label=_("&Continue Installation")
		)
		continue_btn.SetDefault()
		button_sizer.Add(view_new_btn, 0, wx.RIGHT, 10)
		button_sizer.Add(continue_btn, 0)
		main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)

		self.SetSizerAndFit(main_sizer)
		self.Bind(wx.EVT_CLOSE, self._on_close)
		view_new_btn.Bind(wx.EVT_BUTTON, self._on_view_whats_new)


def onInstall():
	done_event = threading.Event()

	def _show_dialog():
		gui.mainFrame.prePopup()
		try:
			prompt = InstallPromptDialog(gui.mainFrame)
			try:
				result = prompt.ShowModal()
			finally:
				prompt.Destroy()
			if result == wx.ID_MORE:
				dialog = WhatsNewDialog(gui.mainFrame)
				try:
					dialog.ShowModal()
				finally:
					dialog.Destroy()
		finally:
			gui.mainFrame.postPopup()
			done_event.set()

	wx.CallAfter(_show_dialog)
	done_event.wait()

