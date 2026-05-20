# Clipboard Content Editor

Penulis: Fauzan January

[Baca dalam Bahasa Inggris](../en/readme.md)

Add-on NVDA ini memungkinkan Anda mengedit teks papan klip (clipboard) saat ini dalam dialog sederhana sebelum menempelkannya di tempat lain. Add-on ini juga berfungsi sebagai manajer papan klip yang canggih dengan riwayat tanpa batas, mode tambal (append mode), dan tindakan cepat untuk menampilkan informasi, membacakan teks, dan membersihkan format.

## Fitur-fitur

- **Clipboard Editor**: Edit teks papan klip saat ini dalam editor multibaris yang dilengkapi dengan fitur Temukan/Ganti, Konversi Huruf (Change Case), dan Pembersih Teks.
- **Clipboard History**: Secara otomatis menyimpan item yang Anda salin ke dalam daftar riwayat tanpa batas dengan kemampuan CRUD (Baca, Edit, Hapus).
- **Append Mode (Mode Tambal)**: Kumpulkan banyak cuplikan teks dengan lancar dengan menggabungkan salinan baru ke papan klip yang sudah ada.
- **Informasi & Suara**: Tampilkan informasi detail (karakter, kata, baris) dan bacakan seluruh teks papan klip tanpa batasan karakter.
- **Simpan ke File**: Simpan konten papan klip Anda langsung menjadi file `.txt`.
- **Command Layer**: Sistem pintasan global yang terpadu untuk mencegah bentrokan tombol dengan aplikasi atau add-on lain.

## Cara Menggunakan

1. Tekan `Ctrl+Alt+C` untuk mengaktifkan command layer dari add-on.
2. Tekan `E` untuk membuka editor.
3. Edit teks, gunakan menu `Tools` untuk mengubah ukuran huruf atau membersihkan teks, atau gunakan fitur Temukan/Ganti.
4. Tekan Simpan (Ctrl+S) untuk memperbarui papan klip dengan konten yang telah diedit.

## Daftar Perintah

- `Ctrl+Alt+C`: Aktifkan mode perintah Clipboard Content Editor
- `F1`: Buka Daftar Perintah atau Dokumentasi Lengkap (saat dalam mode perintah)
- `A`: Aktifkan / Nonaktifkan Mode Tambal (saat dalam mode perintah)
- `E`: Buka Editor Papan Klip (saat dalam mode perintah)
- `R`: Pulihkan Cadangan Editor (saat dalam mode perintah)
- `I`: Ucapkan Informasi Papan Klip (saat dalam mode perintah)
- `S`: Bacakan Konten Papan Klip (saat dalam mode perintah)
- `H`: Buka Manajer Riwayat Papan Klip (saat dalam mode perintah)

## Persyaratan Sistem

- NVDA 2025.3 atau lebih baru (termasuk dukungan penuh untuk NVDA 2026.1 dan Python 64-bit).
- Windows 10 atau lebih baru.

### Pintasan Editor
(Ini hanya berfungsi saat Dialog Editor terbuka)

- `Alt+S` - Menu Suara (ucapkan konten).
- `Alt+I` - Informasi Papan Klip (di dalam menu Tools).
- `Alt+F` - Temukan teks.
- `Alt+R` - Ganti teks.
- `Alt+U` - Ubah ke huruf besar.
- `Alt+L` - Ubah ke huruf kecil.
- `Alt+T` - Ubah ke huruf kapital pada setiap kata (Title case).
- `Alt+W` - Hapus spasi di awal dan akhir teks (Trim whitespace).
- `Alt+E` - Hapus baris kosong.
- `Alt+H` - Hapus tag HTML/Format.
- `Ctrl+S` - Simpan (Tombol Simpan).
- `Ctrl+Shift+S` - Simpan Sebagai (Tombol Simpan Sebagai...).
- `Esc` - Batal (Tombol Batal).

### Pintasan Manajer Riwayat
(Ini hanya berfungsi saat Dialog Riwayat terbuka)

- `Enter` - Pulihkan item yang dipilih ke papan klip.
- `Alt+E` - Buka item yang dipilih di Editor.
- `Alt+D` - Hapus item yang dipilih dari riwayat.
- `Alt+C` - Bersihkan seluruh riwayat.

## Pengaturan

Buka Pengaturan NVDA dan pilih kategori Clipboard Content Editor:

- Bahasa Addon (memungkinkan Anda menggunakan bahasa yang berbeda untuk addon dari bahasa NVDA; memerlukan mulai ulang NVDA).
- Aktifkan suara (Bawaan: diaktifkan).
- Aktifkan mode perlindungan (cadangan papan klip editor).
- Jumlah tingkat cadangan.
- Batas riwayat papan klip (pilihan: 10, 25, 50, 100, Semua; bawaan: 10).

## Catatan

- **Mode Tambal (Append Mode)**: Saat diaktifkan, setiap kali Anda menekan `Ctrl+C`, teks baru akan ditambahkan ke bagian bawah teks papan klip Anda saat ini, alih-alih menggantinya. Ingatlah untuk mematikannya setelah Anda selesai mengumpulkan teks!
- **Manajer Riwayat**: Riwayat melacak semua teks yang Anda salin di seluruh sistem secara otomatis.

## Lisensi

Add-on ini dirilis di bawah GNU General Public License versi 2 (GPL v2).

## Dukungan dan Kontribusi Pengembangan

Jika Anda ingin ikut berkontribusi atau mendukung pengembangan addon ini, Anda dapat melakukannya dengan cara memberi masukan, melaporkan bug, atau pengajuan fitur baru dengan cara menghubungi kontak yang tersedia, membuka issue atau permintaan pull di GitHub, serta berdonasi untuk keberlanjutan pengembangan.

- **PayPal:** [donate@fauzanaja.com](mailto:donate@fauzanaja.com)
- **PayPal.me:** [paypal.me/fauzanjanuary](https://paypal.me/fauzanjanuary)

## Kontak

- Email: [surel@fauzanaja.com](mailto:surel@fauzanaja.com)
- Telegram: [fauzan_january](https://t.me/fauzan_january/)
- Saluran WhatsApp: [fauzan_january](https://whatsapp.com/channel/0029VaFLXIO545upgh6w5h3K)
- Situs Web: [fauzanaja.com](https://fauzanaja.com/)
