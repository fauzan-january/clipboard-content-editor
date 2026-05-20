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
try:
	import config
	if "ClipboardContentEditor" not in config.conf:
		config.conf["ClipboardContentEditor"] = {}
	lang = config.conf["ClipboardContentEditor"].get("language", "default")
	if lang != "default":
		import gettext
		import inspect
		import os
		addon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
		locale_dir = os.path.join(addon_dir, "locale")
		t = gettext.translation("nvda", localedir=locale_dir, languages=[lang])
		frame = inspect.currentframe()
		if frame:
			frame.f_globals["_"] = t.gettext
except Exception:
	pass

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


class DonationDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title=_("Support Clipboard Content Editor Development"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, size=(600, 300))
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Intro Text
		full_text = (
			_("If you find this addon useful in your work or activities, please consider supporting its ongoing development. Your support, no matter how small, is very meaningful in helping develop new features, fix bugs, and maintain the addon for the future.\n\n") +
			"PayPal:\ndonate@fauzanaja.com\n\npaypal.me/fauzanjanuary"
		)
		
		self.txt_full_info = wx.TextCtrl(
			self, 
			value=full_text, 
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.BORDER_SUNKEN
		)
		self.txt_full_info.SetFocus()
		sizer.Add(self.txt_full_info, 1, wx.EXPAND | wx.ALL, 10)
		
		# External Link Buttons
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.btn_paypal = wx.Button(self, label=_("Copy PayPal Email"))
		self.btn_paypal.Bind(wx.EVT_BUTTON, lambda evt: self.copy_to_clipboard("donate@fauzanaja.com"))
		btnSizer.Add(self.btn_paypal, 0, wx.RIGHT, 10)
		
		self.btn_website = wx.Button(self, label=_("Open PayPal Link"))
		self.btn_website.Bind(wx.EVT_BUTTON, lambda evt: self.open_url("https://paypal.me/fauzanjanuary"))
		btnSizer.Add(self.btn_website, 0, wx.RIGHT, 10)
		
		self.btn_close = wx.Button(self, wx.ID_CANCEL, label=_("Close"))
		btnSizer.Add(self.btn_close, 0, wx.LEFT, 20)
		
		sizer.Add(btnSizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
		
		self.SetSizer(sizer)
		self.Centre()

	def copy_to_clipboard(self, text):
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(wx.TextDataObject(text))
			wx.TheClipboard.Close()
			import ui
			ui.message(_("Donation email copied successfully."))
		else:
			import ui
			ui.message(_("Failed to copy donation email."))

	def open_url(self, url):
		import webbrowser
		webbrowser.open(url)

class InstallPromptDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title=_("Clipboard Content Editor Installation"))
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Message
		message = _("Welcome to Clipboard Content Editor! Before continuing the installation, what would you like to do?")
		text = wx.StaticText(self, label=message)
		text.Wrap(500)
		main_sizer.Add(text, 0, wx.ALL, 15)
		
		# Buttons Sizer
		btn_sizer = wx.BoxSizer(wx.VERTICAL)
		
		# 1. See What's New
		self.btn_whats_new = wx.Button(self, label=_("&1. See What's New"))
		self.btn_whats_new.Bind(wx.EVT_BUTTON, self._on_whats_new)
		btn_sizer.Add(self.btn_whats_new, 0, wx.EXPAND | wx.BOTTOM, 10)
		
		# 2. Support Development
		self.btn_support = wx.Button(self, label=_("&2. Support Development (Donate)"))
		self.btn_support.Bind(wx.EVT_BUTTON, self._on_support)
		btn_sizer.Add(self.btn_support, 0, wx.EXPAND | wx.BOTTOM, 10)
		
		# 3. Continue Installation
		self.btn_continue = wx.Button(self, wx.ID_OK, label=_("&3. Continue Installation"))
		self.btn_continue.SetDefault()
		self.btn_continue.Bind(wx.EVT_BUTTON, self._on_continue)
		btn_sizer.Add(self.btn_continue, 0, wx.EXPAND, 0)
		
		main_sizer.Add(btn_sizer, 1, wx.EXPAND | wx.ALL, 15)
		
		self.SetSizerAndFit(main_sizer)
		self.Centre()

	def _on_whats_new(self, evt):
		dlg = WhatsNewDialog(self)
		dlg.ShowModal()
		dlg.Destroy()
		
	def _on_support(self, evt):
		dlg = DonationDialog(self)
		dlg.ShowModal()
		dlg.Destroy()
			
	def _on_continue(self, evt):
		self.EndModal(wx.ID_OK)

def onInstall():
	done_event = threading.Event()

	def _show_dialog():
		gui.mainFrame.prePopup()
		try:
			prompt = InstallPromptDialog(gui.mainFrame)
			prompt.ShowModal()
			prompt.Destroy()
		finally:
			gui.mainFrame.postPopup()
			done_event.set()

	wx.CallAfter(_show_dialog)
	done_event.wait()

