# Cliptboard Content Editor

Penulis: Fauzan January

[Baca dalam Bahasa Inggris](../en/readme.md)

Add-on NVDA ini membantu Anda mengedit teks clipboard saat ini melalui dialog sederhana sebelum ditempelkan ke aplikasi lain. Add-on ini juga menyediakan aksi cepat untuk menampilkan informasi, mencari, dan mengganti teks.

## Apa yang Baru?

- Pintasan global sekarang distandarkan: NVDA+E membuka dialog editor, NVDA+Z memulihkan cadangan papan klip, dan NVDA+I mengumumkan jumlah karakter/kata/baris pada papan klip.
- Semua pintasan global kini bisa diubah lewat pengaturan Input Gestures di NVDA.
- Fitur Clear dihapus sepenuhnya (tombol, shortcut, pengaturan, dan notifikasi) karena pengguna bisa menghapus langsung lewat editor papan klip.
- Fitur Read dihapus sepenuhnya (tombol, shortcut, pengaturan, dan notifikasi) karena NVDA sudah menyediakan pembacaan papan klip lewat NVDA+C.
- Menambahkan tombol Find sebelum Replace, dengan opsi enable/disable terpisah serta pintasan diperbarui (Alt+F untuk Find, Alt+R untuk Replace).
- Replace sekarang menjaga kapitalisasi secara default (mengikuti huruf besar/kecil pada teks yang ditemukan).
- Label checkbox diperbarui menjadi "Case sensitive" dan "Find/Replace whole words only, not part of other words".
- Teks info clipboard kini menjadi "Clipboard information: ...".
- Dokumentasi sekarang menampilkan tautan ke bahasa lain yang tersedia.
- Informasi Apa yang Baru kini tersedia di dokumentasi dan dialog instalasi.
- Informasi dukungan pengembangan dihapus dari dokumentasi dan dialog instalasi.

## Fitur

- Mengedit teks clipboard pada editor multiline.
- Dialog Find untuk mencari teks.
- Mengganti teks di dalam editor.
- Menampilkan informasi (jumlah karakter, kata, dan baris) dari teks clipboard.
- Cadangan clipboard (protect mode) dan pemulihan.
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
- `Esc` - Cancel (tombol Cancel).

Jika clipboard kosong, Information akan mengumumkan "clipboard is empty".

## Pengaturan

Buka NVDA Settings dan pilih kategori add-on:

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
- Telegram: [fauzan_january/](https://t.me/fauzan_january/)
- Situs web: [fauzanaja.com/](https://fauzanaja.com/)
