# Cliptboard Content Editor

Penulis: Fauzan January

Add-on NVDA ini membantu Anda mengedit teks clipboard saat ini melalui dialog sederhana sebelum ditempelkan ke aplikasi lain. Add-on ini juga menyediakan aksi cepat untuk membaca clipboard, menampilkan informasi, serta find/replace.

## Fitur

- Mengedit teks clipboard pada editor multiline.
- Mengosongkan clipboard dengan satu tombol.
- Membaca teks clipboard atau teks terpilih di editor.
- Menampilkan informasi (jumlah karakter, kata, dan baris) dari teks clipboard.
- Find/Replace di dalam editor.
- Cadangan clipboard (protect mode) dan pemulihan.
- Shortcut global untuk Read dan Information.

## Cara pakai

1. Tekan `Ctrl+Alt+C` untuk membuka editor.
2. Edit teks sesuai kebutuhan.
3. Gunakan tombol atau shortcut untuk Read, Information, Find/Replace, Clear, Save, atau Cancel.
4. Tekan Save untuk menyimpan hasil ke clipboard.

## Shortcut

Shortcut global (bisa dipakai di mana saja):

- `Ctrl+Alt+C` - Buka editor clipboard.
- `Alt+R` - Read isi clipboard.
- `Alt+I` - Informasi isi clipboard.
- `Ctrl+Shift+Z` - Pulihkan clipboard dari cadangan (protect mode).

Shortcut di dialog editor:

- `Alt+C` - Clear isi clipboard.
- `Alt+R` - Read teks terpilih atau seluruh teks di editor.
- `Alt+I` - Information untuk teks editor.
- `Alt+F` - Find/Replace.
- `Alt+S` - Save perubahan.
- `Esc` - Cancel.

Jika clipboard kosong, Read dan Information akan mengumumkan "clipboard is empty".

## Pengaturan

Buka NVDA Settings dan pilih kategori add-on:

- Keep shortcuts active when buttons are hidden in editor (default: enabled).
- Enable Clear button in editor.
- Enable Read button in editor.
- Enable Information button in editor.
- Enable Find/Replace button in editor.
- Enable protect mode (clipboard backup).
- Number of backup levels.

## Protect mode (cadangan clipboard)

Saat protect mode aktif, add-on menyimpan riwayat isi clipboard sebelum disimpan. Anda bisa memulihkan isi clipboard sebelumnya dengan `Ctrl+Shift+Z`. Jumlah cadangan yang disimpan diatur oleh "Number of backup levels".

## Catatan

- Jika Anda Clear lalu Save, clipboard akan tersimpan kosong.
- Find/Replace mendukung match case dan hanya mengganti di teks editor.

## Lisensi

Add-on ini dirilis dengan lisensi GNU General Public License versi 2 (GPL v2).

## Dukungan pengembangan

Jika ingin mendukung pengembangan, Anda bisa berdonasi:

- **Kartu kredit (Atas nama: Fauzan)**:
```
106529506491
```
- **Metode donasi lainnya (khusus Indonesia)**:
  [https://fauzanaja.com/berikan-dukungan/](https://fauzanaja.com/berikan-dukungan/)

## Kontak

- Surel: [surel@fauzanaja.com](mailto:surel@fauzanaja.com)
- GitHub: [https://github.com/fauzan-january/](https://github.com/fauzan-january/)
- Situs web: [https://fauzanaja.com/](https://fauzanaja.com/)