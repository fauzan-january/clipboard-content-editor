# Cliptboard Content Editor

Author: Fauzan January

[Read in Indonesian](addon/doc/id/readme.md)

This NVDA add-on lets you edit the current clipboard text in a simple dialog before pasting it elsewhere. It also provides quick actions to show information, find text, and replace text.

## What's New?

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

## Features

- Edit the current clipboard text in a multiline editor.
- Find text with a dedicated Find dialog.
- Replace text within the editor.
- Show information (characters, words, lines) about clipboard text.
- Optional clipboard backup (protect mode) with restore.
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
- `Esc` - Cancel (Cancel button).

If the clipboard is empty, Information will announce "clipboard is empty".

## Settings

Open NVDA Settings and select the add-on category:

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
- Telegram: [fauzan_january/](https://t.me/fauzan_january/)
- Website: [fauzanaja.com/](https://fauzanaja.com/)
