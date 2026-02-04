# Cliptboard Content Editor

Author: Fauzan January

[Read in Indonesian](addon/doc/id/readme.md)

This NVDA add-on lets you edit the current clipboard text in a simple dialog before pasting it elsewhere. It also provides quick actions to show information, find text, and replace text.

## What's New?

- Added **Save As** feature (Ctrl+Shift+S) to the editor, allowing content to be saved as .txt or other file types.
- Added a setting to enable or disable addon sounds.
- Added comprehensive sound feedback to Information, Restore Backup, and Replace All features for consistent audio cues.
- Fixed the "Read in [Language]" links in the documentation to correctly open the HTML files instead of showing file not found errors or opening raw source files.
- The editor buttons are now strictly ordered for better navigation: Information (Alt+I) -> Find -> Replace -> Save -> Save As -> Cancel.

## Features

- Edit the current clipboard text in a multiline editor.
- Find text with a dedicated Find dialog.
- Replace text within the editor.
- Show information (characters, words, lines) about clipboard text.
- Save clipboard content to a file.
- Optional clipboard backup (protect mode) with restore.
- Customizable sound settings.
- Global shortcuts for Information.

## How to use

1. Press `NVDA+E` to open the editor.
2. Edit the text as needed.
3. Use the buttons or shortcuts for Information, Find, Replace, Save (Ctrl+S), or Cancel (Esc).
4. Press Save (Ctrl+S) to update the clipboard with the edited content.

## Shortcuts

Global shortcuts (work anywhere in NVDA):

- `NVDA+E` - Open the clipboard editor.
- `NVDA+I` - Show information about clipboard text.
- `NVDA+Z` - Restore previous clipboard content (protect mode).

Editor shortcuts:
- `Alt+I` - Show information about the editor text.
- `Alt+F` - Find text.
- `Alt+R` - Replace text.
- `Ctrl+S` - Save changes (Save button).
- `Ctrl+Shift+S` - Save content as file (Save As button).
- `Esc` - Cancel (Cancel button).

If the clipboard is empty, Information will announce "clipboard is empty".

## Settings

Open NVDA Settings and select the add-on category:

- Enable sound (default: enabled).
- Keep shortcuts active when buttons are hidden in editor (default: enabled).
- Enable Information button in editor.
- Enable Find button in editor.
- Enable Replace button in editor.
- Enable protect mode (clipboard backup).
- Number of backup levels.

## Protect mode (clipboard backup)

When protect mode is enabled, the add-on stores a history of clipboard content before saving. You can restore the previous clipboard content using `NVDA+Z`. The number of saved backups is controlled by "Number of backup levels".

## Notes

- Find and Replace support match case and work within the editor text only.
- In the Find dialog, type your text and press Esc to jump to the next match.

## License

This add-on is released under the GNU General Public License version 2 (GPL v2).

## Contact

- Email: [surel@fauzanaja.com](mailto:surel@fauzanaja.com)
- Telegram: [fauzan_january](https://t.me/fauzan_january/)
- Website: [fauzanaja.com](https://fauzanaja.com/)
