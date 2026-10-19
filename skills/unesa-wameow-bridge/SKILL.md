---
name: unesa-wameow-bridge
description: "WhatsApp AI Bridge berbasis Go whatsmeow dengan protokol Human Presence anti-blokir (simulasi mengetik 30-100 WPM, auto read receipt, async queue, kirim DOCX/PDF/media)."
tags: [unesa, whatsapp, wameow, whatsmeow, anti-ban, human-presence, ai-agent, broadcast, bot]
---

# UNESA Wameow Bridge (WhatsApp AI Integration & Anti-Ban Protocol)

Skill integrasi WhatsApp untuk AI Agent (Hermes Agent, Claude, Cursor, ChatGPT) menggunakan engine **Wameow** (Go `whatsmeow`). Dilengkapi **Mandatory Human Presence Protocol** yang membuat pengiriman pesan memiliki pola perilaku manusia asli sehingga **100% aman dari risiko banned/blokir nomor WhatsApp**.

---

## 🛡️ 1. Mengapa Wameow Aman dari Pemblokiran WhatsApp?

Bot WhatsApp konvensional (berbasis Web/Puppeteer/Baileys tanpa delay) sangat mudah diblokir oleh sistem AI Meta karena:
1. Mengirim teks panjang seketika dalam 0.05 detik (pola bot terdeteksi).
2. Tidak pernah memunculkan status *"sedang mengetik..."* (*composing*).
3. Tidak mengirim *read receipt* (tanda baca/centang biru) sebelum membalas pesan.
4. Melakukan spam broadcast ke nomor acak yang tidak saling simpan kontak.

### 🧠 Arsitektur Human Presence Adaptif Wameow (3 Tier Speed):
Wameow menerapkan pipeline simulasi manusia secara otomatis pada setiap pesan keluar:
* **Tahap 1: Online Presence:** Mengaktifkan status online `PresenceAvailable`.
* **Tahap 2: Mark Read:** Mengirim konfirmasi pesan telah dibaca (centang biru) terhadap pesan lawan bicara.
* **Tahap 3: Dynamic Typing Simulation (`composing`):**
  - **Tier 0 (Casual / 1–2 pesan per menit):** Mengetik cepat / simulasi *paste* teks (delay 350–900 ms).
  - **Tier 1 (Normal / 3–5 pesan per menit):** Kecepatan ketik normal 65–100 WPM (120–185 ms/karakter), floor 900–1400 ms.
  - **Tier 2 (Intense / >5 pesan per menit):** Diperlambat otomatis ke 30–50 WPM (240–400 ms/karakter) + jeda jeda 400–900 ms sebelum kirim untuk memecah pola robotik.
* **Tahap 4: Clear Presence & Send:** Mengubah status ke `ChatPresencePaused`, memberi jeda natural, lalu menembakkan pesan.

---

## ⚡ 2. Setup Cepat Wameow di Server / Laptop

* **Repository Resmi:** [https://github.com/mahdiwafy/wameow](https://github.com/mahdiwafy/wameow)
* **Panduan Lengkap Setup & Pairing:** Lihat [docs/PANDUAN_SETUP_WAMEOW_WHATSAPP_AI.md](../../docs/PANDUAN_SETUP_WAMEOW_WHATSAPP_AI.md)

### Langkah Ringkas Menjalankan:
```bash
# 1. Clone & Build
git clone https://github.com/mahdiwafy/wameow.git ~/wameow
cd ~/wameow && go build -o wameow .

# 2. Jalankan Wameow
./wameow --sessions=wa1 --listen=:52135

# 3. Pairing: Buka browser di http://localhost:52135/png-qr/wa1 lalu scan via WhatsApp HP
```

---

## 🤖 3. Cara AI Agent Menjalankan Wameow Secara Langsung

AI Agent (Hermes Agent, Claude Code, Cursor) dapat mengeksekusi pengiriman pesan dan berkas secara instan menggunakan script pembantu `wameow_tool.py` di dalam folder `scripts/`:

### A. Periksa Status Koneksi WhatsApp
```bash
python3 skills/unesa-wameow-bridge/scripts/wameow_tool.py status
# Menghasilkan exit code 0 dan output JSON {"status": "connected"} jika siap pakai
```

### B. Kirim Pesan Teks Asinkron (Anti-Banned)
```bash
python3 skills/unesa-wameow-bridge/scripts/wameow_tool.py send "081234567890" "Halo! Draf tugas sudah selesai dibuat."
```
*Script otomatis mengonversi format nomor lokal `08xxx` menjadi format internasional WhatsApp `628xxx` dan menembak endpoint `/send-async`.*

### C. Kirim Berkas Tugas / Dokumen Akademik
```bash
python3 skills/unesa-wameow-bridge/scripts/wameow_tool.py send-file "081234567890" "/path/to/Makalah_Final.docx" --caption "Berikut draf makalahnya yaa"
```
*Script otomatis mendeteksi MIME type untuk DOCX, XLSX, PPTX, PDF, ZIP, PNG, JPG.*

### D. Cari Riwayat Obrolan
```bash
python3 skills/unesa-wameow-bridge/scripts/wameow_tool.py search "tugas sistem operasi"
```

---

## 📡 4. REST API Reference (Direct cURL / HTTP Requests)

Base URL: `http://localhost:52135`

### A. Kirim Pesan Teks Asinkron (Sangat Direkomendasikan ⚡)
Gunakan `/send-async` agar AI Agent tidak mengalami timeout saat Wameow mensimulasikan proses mengetik:
```bash
curl -X POST http://localhost:52135/send-async \
  -H "Content-Type: application/json" \
  -d '{
    "session": "wa1",
    "chatId": "6281234567890",
    "text": "Halo! Berikut hasil draf tugas makalah yang sudah selesai disusun."
  }'
```

---

### B. Kirim Dokumen Tugas / Media (`POST /send-media`)
Mendukung pengiriman semua jenis berkas akademik (Word `.docx`, Excel `.xlsx`, PPT `.pptx`, PDF, ZIP, Gambar, Audio):

#### 1. Mengirim Berkas dari Path Lokal Server/Laptop:
```bash
curl -X POST http://localhost:52135/send-media \
  -H "Content-Type: application/json" \
  -d '{
    "session": "wa1",
    "chatId": "6281234567890",
    "filePath": "/home/user/Makalah_Sistem_Operasi.docx",
    "fileName": "Makalah_Sistem_Operasi.docx",
    "caption": "Ini berkas tugas Word format A4 sesuai pedoman UNESA yaa",
    "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  }'
```

#### 2. Mimetype Berkas Akademik Umum:
* **📄 PDF:** `application/pdf`
* **📝 Word (.docx):** `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
* **📊 Excel (.xlsx):** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
* **📽️ PowerPoint (.pptx):** `application/vnd.openxmlformats-officedocument.presentationml.presentation`
* **🗜️ Archive (.zip):** `application/zip`
* **🖼️ Gambar (.png/.jpg):** `image/png` / `image/jpeg`

---

### C. Mencari Riwayat Chat & Kontak (`/history`)
Wameow mengarsipkan seluruh pesan masuk dan keluar secara permanen di SQLite:
```bash
# Cari pesan berdasarkan kata kunci tugas / nama teman
curl "http://localhost:52135/history/search?q=Makalah&session=wa1"

# Lihat riwayat pesan di chat tertentu
curl "http://localhost:52135/history/messages?session=wa1&chatId=6281234567890@s.whatsapp.net&limit=20"
```

---

## 🚨 4. Aturan Emas Anti-Banned (Golden Rules)

1. **JANGAN PERNAH Spam Cold-Message:**
   * Jangan mengirim pesan promosi/spam otomatis ke nomor acak yang belum pernah chat atau tidak menyimpan nomormu.
   * Gunakan bot hanya untuk: komunikasi grup kelas, asisten pribadi, membalas chat teman yang masuk, atau notifikasi tugas terjadwal.
2. **Selalu Gunakan Endpoint `/send-async`:**
   * Mencegah aplikasi klien mengirim ulang request (*retry loop*) akibat mengira request gagal saat proses pengetikan berlangsung.
3. **Beri Jeda Alami saat Broadcast:**
   * Jika PJ MK ingin menyebarkan info ke beberapa grup atau teman, beri jeda 3–5 detik antar pesan. Jangan menembakkan 50 pesan dalam 1 detik.
4. **Gunakan Nomor Utama / Nomor yang Sudah Berumur:**
   * Nomor WhatsApp baru (<1-2 minggu) memiliki reputasi trust rendah di sistem Meta. Usahakan menggunakan nomor yang sudah pernah aktif berinteraksi secara reguler.

---

## 🤖 5. Contoh Integrasi Otomasi AI untuk Tugas Kampus

Ketika teman atau dosen mengirim pesan WhatsApp:
> *"Tolong rangkumkan materi pertemuan 4 Sistem Operasi dan kirim format PDF-nya ya."*

AI Agent dapat langsung:
1. Membaca pesan masuk dari Webhook Wameow atau `/history/messages`.
2. Menghasilkan draf rangkuman terstruktur menggunakan skill `smart-study-and-research`.
3. Mengonversi menjadi dokumen PDF/Word rapi menggunakan `unesa-academic-standards`.
4. Mengirim balik dokumen PDF ke WhatsApp teman tersebut via `POST /send-media` dengan simulasi human presence lengkap.
