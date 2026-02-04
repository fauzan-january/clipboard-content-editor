# Cliptboard Content Editor

Penulis: Fauzan January

[Baca dalam Bahasa Inggris](../en/readme.md)

Add-on NVDA ini membantu Anda mengedit teks clipboard saat ini melalui dialog sederhana sebelum ditempelkan ke aplikasi lain. Add-on ini juga menyediakan aksi cepat untuk menampilkan informasi, mencari, dan mengganti teks.

## Apa yang Baru?

- Menambahkan fitur **Save As** (Ctrl+Shift+S) ke editor, konten bisa disimpan sebagai .txt atau tipe file lainnya.
- Menambahkan opsi untuk mengaktifkan atau menonaktifkan suara add-on.
- Menambahkan umpan balik suara pada fitur Information, Restore Backup, dan Replace All agar konsisten.
- Memperbaiki link "Read in [Language]" di dokumentasi yang sebelumnya error (file not found) atau membuka source file mentah.
- Urutan tombol editor dirapikan: Information (Alt+I) -> Find -> Replace -> Save -> Save As -> Cancel.

## Fitur

- Mengedit teks clipboard pada editor multiline.
- Dialog Find untuk mencari teks.
- Mengganti teks di dalam editor.
- Menampilkan informasi (jumlah karakter, kata, dan baris) dari teks clipboard.
- Menyimpan konten clipboard ke file.
- Cadangan clipboard (protect mode) dan pemulihan.
- Pengaturan suara yang dapat disesuaikan.
- Shortcut global untuk Information.

## Cara pakai

1. Tekan `NVDA+E` untuk membuka editor.
2. Edit teks sesuai kebutuhan.
3. Gunakan tombol atau shortcut untuk Information, Find, Replace, Save (Ctrl+S), atau Cancel (Esc).
4. Tekan Save (Ctrl+S) untuk menyimpan hasil ke clipboard.

## Shortcut

Shortcut global (bisa dipakai di mana saja):

- `NVDA+E` - Buka editor clipboard.
- `NVDA+I` - Informasi isi clipboard.
- `NVDA+Z` - Pulihkan clipboard dari cadangan (protect mode).

Shortcut di dialog editor:
- `Alt+I` - Information untuk teks editor.
- `Alt+F` - Cari teks (Find).
- `Alt+R` - Ganti teks (Replace).
- `Ctrl+S` - Save perubahan (tombol Save).
- `Ctrl+Shift+S` - Simpan konten sebagai file (tombol Save As).
- `Esc` - Cancel (tombol Cancel).

Jika clipboard kosong, Information akan mengumumkan "clipboard is empty".

## Pengaturan

Buka NVDA Settings dan pilih kategori add-on:

- Enable sound (default: enabled).
- Keep shortcuts active when buttons are hidden in editor (default: enabled).
- Enable Information button in editor.
- Enable Find button in editor.
- Enable Replace button in editor.
- Enable protect mode (clipboard backup).
- Number of backup levels.

## Protect mode (cadangan clipboard)

Saat protect mode aktif, add-on menyimpan riwayat isi clipboard sebelum disimpan. Anda bisa memulihkan isi clipboard sebelumnya dengan `NVDA+Z`. Jumlah cadangan yang disimpan diatur oleh "Number of backup levels".

## Catatan

- Find dan Replace mendukung match case dan hanya bekerja di teks editor.
- Di dialog Find, ketik teks lalu tekan Esc untuk langsung menuju kecocokan berikutnya.

## Lisensi

Add-on ini dirilis dengan lisensi GNU General Public License versi 2 (GPL v2).

## Kontak

- Surel: [surel@fauzanaja.com](mailto:surel@fauzanaja.com)
- Telegram: [fauzan_january](https://t.me/fauzan_january/)
- Situs web: [fauzanaja.com](https://fauzanaja.com/)
