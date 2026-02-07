<<<<<<< HEAD
## Changelog - Version 1.2.1
=======
## Changelog - Version 1.2.0
>>>>>>> 8f9247c0e47cefdc23e7fb1ca3628dc33eec20c4

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
