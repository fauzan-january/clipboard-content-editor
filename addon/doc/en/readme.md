# Cliptboard Content Editor

Author: Fauzan January

This NVDA add-on lets you edit the current clipboard text in a simple dialog before pasting it elsewhere. It also provides quick actions to read the clipboard, show information, and find/replace text.

## Features

- Edit the current clipboard text in a multiline editor.
- Clear clipboard content with a single button.
- Read clipboard text or selected text in the editor.
- Show information (characters, words, lines) about clipboard text.
- Find and replace inside the editor.
- Optional clipboard backup (protect mode) with restore.
- Global shortcuts for Read and Information.

## How to use

1. Press `Ctrl+Alt+C` to open the editor.
2. Edit the text as needed.
3. Use the buttons or shortcuts for Read, Information, Find/Replace, Clear, Save, or Cancel.
4. Press Save to update the clipboard with the edited content.

## Shortcuts

Global shortcuts (work anywhere in NVDA):

- `Ctrl+Alt+C` - Open the clipboard editor.
- `Alt+R` - Read clipboard text.
- `Alt+I` - Show information about clipboard text.
- `Ctrl+Shift+Z` - Restore previous clipboard content (protect mode).

Editor shortcuts:

- `Alt+C` - Clear clipboard content.
- `Alt+R` - Read selection or full text in the editor.
- `Alt+I` - Show information about the editor text.
- `Alt+F` - Find/Replace.
- `Alt+S` - Save changes.
- `Esc` - Cancel.

If the clipboard is empty, Read and Information will announce "clipboard is empty".

## Settings

Open NVDA Settings and select the add-on category:

- Keep shortcuts active when buttons are hidden in editor (default: enabled).
- Enable Clear button in editor.
- Enable Read button in editor.
- Enable Information button in editor.
- Enable Find/Replace button in editor.
- Enable protect mode (clipboard backup).
- Number of backup levels.

## Protect mode (clipboard backup)

When protect mode is enabled, the add-on stores a history of clipboard content before saving. You can restore the previous clipboard content using `Ctrl+Shift+Z`. The number of saved backups is controlled by "Number of backup levels".

## Notes

- Clearing and saving will store an empty clipboard if you choose to save it.
- Find/Replace supports match case and replaces within the editor text only.

## License

This add-on is released under the GNU General Public License version 2 (GPL v2).

## Support Development

If you want to support development, you can donate:

- **Credit card (Name: Fauzan)**:
```
106529506491
```
- **Other donation methods (Indonesia only)**:
  [https://fauzanaja.com/berikan-dukungan/](https://fauzanaja.com/berikan-dukungan/)
  
## Contact

- Email: [surel@fauzanaja.com](mailto:surel@fauzanaja.com)
- GitHub: [https://github.com/fauzan-january/](https://github.com/fauzan-january/)
- Website: [https://fauzanaja.com/](https://fauzanaja.com/)