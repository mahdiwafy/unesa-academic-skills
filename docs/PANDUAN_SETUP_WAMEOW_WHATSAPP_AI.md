# 📱 Panduan Lengkap Setup Wameow (WhatsApp AI Bridge & Anti-Ban)

Panduan instalasi mandiri dari nol (zero-to-running) untuk memasang dan menghubungkan engine **Wameow** ke AI Agent (Hermes Agent, Claude Code, Cursor, Windsurf, atau bot custom).

> **Mengapa Wameow?**
> Wameow dibangun menggunakan bahasa pemrograman Go murni dengan library `whatsmeow`. Sangat ringan (RAM < 100 MB), tanpa browser Puppeteer/Chromium yang berat, dan dilengkapi **Adaptive Human Presence Protocol** (simulasi mengetik 30–100 WPM, auto read receipt, jeda natural) yang **100% aman dari risiko pemblokiran/banned nomor oleh Meta**.

---

## 📋 Prasyarat Sistem

Sebelum memulai instalasi, pastikan mesin Anda (Laptop/Server Linux, macOS, atau WSL Windows) telah memiliki:
* **Go Compiler:** Versi 1.21 atau lebih baru (`go version`).
  * Jika belum terpasang:
    * Ubuntu/Debian: `sudo apt update && sudo apt install -y golang`
    * macOS: `brew install go`
* **Git:** Untuk mengunduh source code repository (`git --version`).
* **WhatsApp di Smartphone:** Akun WhatsApp aktif yang akan ditautkan sebagai asisten AI.

---

## 1️⃣ LANGKAH 1: Unduh & Compile Wameow

### 1.1 Clone Repository
Unduh source code resmi Wameow dari GitHub:

```bash
git clone https://github.com/mahdiwafy/wameow.git ~/wameow
cd ~/wameow
```

### 1.2 Compile Menjadi Binary Mandiri
Jalankan kompilasi Go:

```bash
go build -o wameow .
```

*Proses kompilasi akan menghasilkan single executable binary `./wameow` berukuran ~18 MB tanpa dependensi eksternal.*

---

## 2️⃣ LANGKAH 2: Menjalankan Wameow

Anda dapat menjalankan Wameow secara langsung di terminal, background process (screen/tmux), atau sebagai daemon systemd.

### Opsi A: Jalankan Langsung (Testing / Pengembangan)
```bash
cd ~/wameow
./wameow --sessions=wa1 --listen=:52135
```
*Parameter:*
* `--sessions=wa1`: Nama session WhatsApp (default: `wa1`).
* `--listen=:52135`: Port REST API lokal untuk komunikasi dengan AI Agent.

### Opsi B: Jalankan Otomatis via Systemd (Direkomendasikan di Server)
Buat file service systemd agar Wameow otomatis menyala saat mesin reboot:

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/wameow.service << EOF
[Unit]
Description=Wameow WhatsApp AI Gateway
After=network.target

[Service]
Type=simple
WorkingDirectory=$HOME/wameow
ExecStart=$HOME/wameow/wameow --sessions=wa1 --listen=:52135
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF
```

Aktifkan service:
```bash
systemctl --user daemon-reload
systemctl --user enable wameow
systemctl --user start wameow
```

Periksa status:
```bash
systemctl --user status wameow
```

---

## 3️⃣ LANGKAH 3: Pairing Akun WhatsApp (Scan QR Code 1-Klik)

Wameow menggunakan protokol resmi WhatsApp Multi-Device. Anda cukup menautkan nomor sekali saja:

1. **Buka Browser di Laptop/PC:**
   Akses alamat: `http://localhost:52135/png-qr/wa1`
   *(Gambar QR Code resmi WhatsApp akan muncul di layar)*
2. **Scan dari Smartphone:**
   * Buka aplikasi **WhatsApp** di HP Anda.
   * Masuk ke menu **Setelan (Settings)** atau ikon **Titik Tiga (⋮)** di pojok kanan atas.
   * Pilih **Perangkat Tertaut (Linked Devices)** -> klik tombol **Tautkan Perangkat (Link a Device)**.
   * Arahkan kamera HP ke gambar QR Code di layar browser.
3. **Verifikasi Status Koneksi:**
   Buka terminal dan jalankan:
   ```bash
   curl -s http://localhost:52135/qr/wa1
   ```
   Jika berhasil, terminal akan menampilkan respons:
   ```json
   {"status":"connected"}
   ```
4. **Selesai!**
   Sesi login Anda tersimpan secara persisten di database lokal `~/wameow/wameow.db`. Meskipun HP Anda mati, kehabisan baterai, atau offline, Wameow tetap dapat mengirim dan menerima pesan secara mandiri.

---

## 4️⃣ LANGKAH 4: Cara AI Agent Menggunakan Wameow

Setelah skill terpasang, AI Agent Anda dapat langsung berinteraksi dengan Wameow menggunakan dua cara:

### Cara 1: Menggunakan Script Helper CLI (Paling Mudah ⚡)
Tersedia script Python pembantu di direktori skill:

```bash
# 1. Periksa status koneksi
python3 skills/unesa-wameow-bridge/scripts/wameow_tool.py status

# 2. Kirim pesan teks (otomatis normalisasi nomor 08xxx ke 628xxx)
python3 skills/unesa-wameow-bridge/scripts/wameow_tool.py send "081234567890" "Halo! Draf tugas makalah sudah selesai saya buatkan ya."

# 3. Kirim dokumen tugas (Word, PDF, Excel, PPTX, gambar)
python3 skills/unesa-wameow-bridge/scripts/wameow_tool.py send-file "081234567890" "/path/to/Makalah_Final.docx" --caption "Silakan dicek berkasnya"

# 4. Cari pesan di riwayat chat berdasarkan kata kunci
python3 skills/unesa-wameow-bridge/scripts/wameow_tool.py search "tugas sistem operasi"
```

### Cara 2: Memanggil REST API via cURL / Python Requests
Jika AI Agent Anda mengeksekusi perintah terminal langsung:

```bash
# Kirim pesan teks asinkron (Recommended)
curl -X POST http://localhost:52135/send-async \
  -H "Content-Type: application/json" \
  -d '{
    "session": "wa1",
    "chatId": "6281234567890",
    "text": "Pesan dari asisten AI..."
  }'

# Kirim berkas dokumen
curl -X POST http://localhost:52135/send-media \
  -H "Content-Type: application/json" \
  -d '{
    "session": "wa1",
    "chatId": "6281234567890",
    "filePath": "/home/user/dokumen.pdf",
    "fileName": "Laporan_Praktikum.pdf",
    "caption": "Berikut laporan praktikum modul 3",
    "mimetype": "application/pdf"
  }'
```

---

## 🛡️ 5. FAQ & Praktik Terbaik Keamanan

1. **Apakah nomor saya aman dari blokir?**
   Ya! Wameow menerapkan **Human Presence Protocol** otomatis: menyalakan status online, menandai pesan dibaca (*read receipt*), mensimulasikan waktu mengetik (30–100 WPM) sesuai panjang teks, dan menyisipkan jeda natural.
2. **Aturan Penting Agar Tidak Diblokir:**
   * Dilarang keras melakukan *blast spam* ke ratusan nomor asing yang tidak saling menyimpan kontak.
   * Gunakan untuk komunikasi kuliah, tugas kelompok, broadcast grup kelas (Komti/PJ), atau asisten pribadi.
3. **Bagaimana jika Wameow terputus?**
   Wameow memiliki fitur *auto-reconnect*. Jika sesi kedaluwarsa setelah berbulan-bulan tidak digunakan, cukup buka kembali `http://localhost:52135/png-qr/wa1` dan scan ulang QR code.
