# Clipboard Content Editor Changelog

## Version 1.3.0

- Added full compatibility for NVDA 2026.1 (Python 64-bit).
- Refactored all global shortcuts into a unified Command Layer (`Ctrl+Alt+C`) to prevent conflicts with other addons and applications. Press `F1` after the command layer trigger to view all available commands in a dialog.
- Introduced an unlimited Clipboard History manager with complete CRUD (Create, Read, Update, Delete) capabilities. Press `H` in the command layer to view and manage past clipboard items.
- Added Append Mode (`A` in the command layer) which allows you to seamlessly collect multiple texts by concatenating new copies to the existing clipboard.
- Restructured the Editor dialog by moving Information, Find, and Replace into a dedicated "Tools" menu alongside *Change Case* (UPPERCASE, lowercase, Title Case), *Text Cleaner* (Trim Whitespace, Remove Empty Lines, Strip Formatting), and a new *Speech* option.
- Restored the ability to speak clipboard content without character limit (`S` in the command layer).
- Added confirmation dialogs before deleting or clearing items in the Clipboard History manager.
- Added settings to configure the maximum Clipboard History size and override the addon's display language independently of NVDA.
- Fixed a bug where the Editor dialog would freeze or hang after successfully saving a file via "Save As...".
- Enhanced the F1 help menu to display an inline command list dialog or open the full HTML README documentation.
- Integrated a Development Support (PayPal donation) dialog into the installation flow.
- Added paragraph counting to the Information feature (characters, words, lines, and paragraphs).

## Changelog - Version 1.2.3

- Added Arabic language support.
- No other feature update.

## Changelog - Version 1.2.2

- Added **Save As** feature (Ctrl+Shift+S) to the editor, allowing content to be saved as .txt or other file types.
- Added a setting to enable or disable addon sounds.
- Added comprehensive sound feedback to Information, Restore Backup, and Replace All features for consistent audio cues.
- Fixed the "Read in [Language]" links in the documentation to correctly open the HTML files instead of showing file not found errors or opening raw source files.
- The editor buttons are now strictly ordered for better navigation: Information -> Find -> Replace -> Save -> Save As -> Cancel.

## Changelog - Version 1.1.0

- Global shortcuts are now standardized: NVDA+E opens the editor dialog, NVDA+Z restores clipboard backups, and NVDA+I announces clipboard character/word/line counts.
- Global shortcuts can now be reassigned via NVDA Input Gestures.
- The Clear feature has been removed entirely (button, shortcut, settings, and notifications) because you can clear text directly in the clipboard editor.
- The Read feature has been removed entirely (button, shortcut, settings, and notifications) because NVDA already provides clipboard reading via NVDA+C.
- A Find button was added before Replace, with separate enable/disable options and updated shortcuts (Alt+F for Find, Alt+R for Replace).
- Replace now preserves case by default, matching the capitalization of the found text.
- Checkbox labels were updated to "Case sensitive" and "Find/Replace whole words only, not part of other words".
- The clipboard info message now reads "Clipboard information: ...".
- Documentation now includes links to other available languages.
- What's New information is now available in both the documentation and the installation dialog.
- Development support information has been removed from the documentation and installation dialog.

## Changelog - Version 1.0.0

- Initial release.
- Added **Clipboard Editor** dialog with the following features:
  - Speech
  - Information
  - Find/Replace
  - Clear
  - Save
  - Cancel
- Introduced global shortcuts for:
  - Opening the editor
  - Speaking clipboard
  - Showing clipboard information
- Implemented **Clipboard Backup (Protect Mode)** with restore functionality.
- Added settings to configure:
  - Button visibility
  - Shortcut behavior
