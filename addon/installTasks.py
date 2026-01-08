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

addonHandler.initTranslation()

DONATION_CARD_NUMBER = "106529506491"
DONATION_CARD_NAME = "Fauzan"
DONATION_PAGE_URL = "https://fauzanaja.com/berikan-dukungan/"


class DonationDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title=_("Clipboard Content Editor - Donation"))
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		message_lines = [
			_("Thank you for using Clipboard Content Editor."),
			_("If you would like to support development, you can donate using:"),
			_("Credit card: {number}").format(number=DONATION_CARD_NUMBER),
			_("Name: {name}").format(name=DONATION_CARD_NAME),
			_("Other methods (Indonesia):"),
			DONATION_PAGE_URL,
		]
		info_text = wx.StaticText(self, label="\n".join(message_lines))
		info_text.Wrap(520)
		main_sizer.Add(info_text, 0, wx.ALL | wx.EXPAND, 15)

		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		open_link_btn = wx.Button(self, label=_("Open donation &page"))
		open_link_btn.Bind(wx.EVT_BUTTON, self._on_open_link)
		button_sizer.Add(open_link_btn, 0, wx.RIGHT, 10)

		copy_btn = wx.Button(self, label=_("&Copy card number"))
		copy_btn.Bind(wx.EVT_BUTTON, self._on_copy_card)
		button_sizer.Add(copy_btn, 0, wx.RIGHT, 10)

		continue_btn = wx.Button(self, label=_("&Continue Installation"))
		continue_btn.Bind(wx.EVT_BUTTON, self._on_continue)
		continue_btn.SetDefault()
		button_sizer.Add(continue_btn, 0)

		main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		self.SetSizerAndFit(main_sizer)
		self.Bind(wx.EVT_CLOSE, self._on_close)

	def _on_open_link(self, evt):
		try:
			os.startfile(DONATION_PAGE_URL)
		except Exception:
			wx.MessageBox(
				_("Unable to open the donation page right now."),
				_("Donation"),
				wx.OK | wx.ICON_WARNING,
			)

	def _on_copy_card(self, evt):
		try:
			if wx.TheClipboard.Open():
				try:
					wx.TheClipboard.SetData(wx.TextDataObject(DONATION_CARD_NUMBER))
				finally:
					wx.TheClipboard.Close()
				wx.MessageBox(
					_("Card number copied to clipboard."),
					_("Donation"),
					wx.OK | wx.ICON_INFORMATION,
				)
				return
		except Exception:
			pass
		wx.MessageBox(
			_("Unable to copy the card number right now."),
			_("Donation"),
			wx.OK | wx.ICON_WARNING,
		)

	def _on_continue(self, evt):
		self.EndModal(wx.ID_OK)

	def _on_close(self, evt):
		self.EndModal(wx.ID_OK)


def onInstall():
	done_event = threading.Event()

	def _show_dialog():
		gui.mainFrame.prePopup()
		try:
			dialog = DonationDialog(gui.mainFrame)
			dialog.ShowModal()
		finally:
			dialog.Destroy()
			gui.mainFrame.postPopup()
			done_event.set()

	wx.CallAfter(_show_dialog)
	done_event.wait()

