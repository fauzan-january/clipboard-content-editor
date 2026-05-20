# Clipboard Content Editor

Author: Fauzan January

[Read in Indonesian](addon/doc/id/readme.md)

This NVDA add-on lets you edit the current clipboard text in a simple dialog before pasting it elsewhere. It also acts as a powerful clipboard manager with unlimited history, append mode, and quick actions to show information, speak, and format text.

## Features

- **Clipboard Editor**: Edit the current clipboard text in a multiline editor with Find/Replace, Change Case, and Text Cleaner tools.
- **Clipboard History**: Automatically saves your copied items into an unlimited history list with CRUD (Create, Read, Update, Delete) capabilities.
- **Append Mode**: Collect multiple text snippets seamlessly by automatically concatenating new copies to the existing clipboard.
- **Information & Speech**: Show detailed information (characters, words, lines) and speak the entire clipboard text.
- **Save to File**: Save your clipboard content directly to a `.txt` file.
- **Command Layer**: A unified global shortcut system to prevent keyboard conflicts.

## How to use

1. Press `Ctrl+Alt+C` to activate the add-on's command layer.
2. Press `E` to open the editor.
3. Edit the text, use `Tools` to change casing or clean text, or use Find/Replace.
4. Press Save (Ctrl+S) to update the clipboard with the edited content.

## Commands

- `Ctrl+Alt+C`: Activate Clipboard Content Editor command layer
- `F1`: Open Command List or Full Documentation (when in command layer)
- `A`: On / Off Append Mode (when in command layer)
- `E`: Open Clipboard Editor (when in command layer)
- `R`: Restore Editor Backup (when in command layer)
- `I`: Say Clipboard Information (when in command layer)
- `S`: Speak Clipboard Content (when in command layer)
- `H`: Open Clipboard History Manager (when in command layer)

## System Requirements

- NVDA 2025.3 or later (including full support for NVDA 2026.1 and 64-bit Python).
- Windows 10 or later.

### Editor Shortcuts
(These work only when the Editor Dialog is open)

- `Alt+T` - Open Tools Menu (Change Case, Text Cleaner).
- `Alt+I` - Show information about the editor text.
- `Alt+F` - Find text.
- `Alt+R` - Replace text.
- `Ctrl+S` - Save changes (Save button).
- `Ctrl+Shift+S` - Save content as file (Save As button).
- `Esc` - Cancel (Cancel button).

### History Manager Shortcuts
(These work only when the History Dialog is open)

- `Enter` - Restore the selected item to the clipboard.
- `Alt+E` - Open the selected item in the Editor.
- `Alt+D` - Delete the selected item from history.
- `Alt+C` - Clear all history.

## Settings

Open NVDA Settings and select the Clipboard Content Editor category:

- Addon language (allows you to use a different language for the addon than NVDA; requires NVDA restart).
- Enable sound (default: enabled).
- Enable protect mode (editor clipboard backup).
- Number of backup levels.
- Clipboard history limit (options: 10, 25, 50, 100, All; default: 10).

## Notes

- **Append Mode**: When enabled, every `Ctrl+C` you press will add the new text to the bottom of your current clipboard instead of replacing it. Remember to turn it off after you finish collecting text!
- **History Manager**: The history tracks all text you copy across your system automatically. 

## License

This add-on is released under the GNU General Public License version 2 (GPL v2).

## Support and Contribution

If you want to contribute or support the development of this addon, you can do so by providing feedback, reporting bugs, or suggesting new features by contacting the available contacts, opening an issue or pull request on GitHub, as well as donating for continued development.

- **PayPal:** [donate@fauzanaja.com](mailto:donate@fauzanaja.com)
- **PayPal.me:** [paypal.me/fauzanjanuary](https://paypal.me/fauzanjanuary)

## Contact

- Email: [surel@fauzanaja.com](mailto:surel@fauzanaja.com)
- Telegram: [fauzan_january](https://t.me/fauzan_january/)
- WhatsApp Channel: [fauzan_january](https://whatsapp.com/channel/0029VaFLXIO545upgh6w5h3K)
- Website: [fauzanaja.com](https://fauzanaja.com/)
