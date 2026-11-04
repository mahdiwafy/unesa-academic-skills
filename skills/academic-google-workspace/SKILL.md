---
name: academic-google-workspace
description: "Akses dan otomasi ekosistem Google: Google Sheets, Docs, Drive, Photos, Calendar, Tasks, Classroom, dan Gmail untuk kebutuhan studi & tugas."
tags: [unesa, google, workspace, drive, docs, sheets, photos, calendar, tasks, classroom, sso, oauth]
---

# Academic Google Workspace Suite (Sheets, Docs, Drive, Photos, Calendar, Tasks)

Skill integrasi resmi untuk menghubungkan AI Agent ke seluruh ekosistem layanan Google mahasiswa dan civitas akademika:
* **Google Sheets:** Membaca, memperbarui, menambah baris data, dan rekapitulasi nilai/praktikum.
* **Google Docs:** Membaca dan membuat naskah makalah, tugas akhir, serta draf laporan.
* **Google Drive:** Pencarian berkas, unduh materi kuliah, unggah tugas, dan manajemen folder.
* **Google Photos:** Akses foto dokumentasi kegiatan, scan KTM/kartu ujian, dan media tugas.
* **Google Calendar & Tasks:** Sinkronisasi jadwal kuliah dan batas waktu (deadline) tugas (Personal & SSO Kampus).
* **Google Classroom & Gmail:** Cek pengumuman kelas, tugas coursework, dan komunikasi formal dosen.

---

## ⚡ 1. Kredensial Project Pre-Configured (Agent Connect)

Pengguna **TIDAK PERLU** lagi membuat project rumit di Google Cloud Console atau mengunduh file JSON secara manual. Repositori ini telah menyertakan kredensial Desktop Application resmi:

* **Nama Aplikasi Resmi di Layar Login:** **`Agent Connect`** (Project `leo-project-498200`).
* **File Kredensial Default:** `~/.hermes/google_client_secret.json` (otomatis digenerate/disalin saat instalasi).
* **Dukungan Dua Akun:**
  - **Akun Personal:** `google_token_personal.json` (default untuk kalender dan drive pribadi).
  - **Akun SSO Kampus (`@mhs.unesa.ac.id`):** `google_token_sso.json` (untuk tugas kampus dan classroom).

---

## 🔑 2. Panduan Setup & Login Google OAuth

### Langkah 1: Buat Link Login
```bash
python3 skills/academic-google-workspace/scripts/setup_google.py --auth-url --account personal
```
*(Ganti `--account sso` jika ingin menautkan akun email kampus UNESA).*

### Langkah 2: Otorisasi di Browser
1. Buka tautan yang muncul di browser.
2. Login dan centang semua izin akses (Drive, Docs, Sheets, Photos, Calendar, Tasks).
3. Setelah klik Setuju, salin URL redirect (`http://localhost/?code=...`) atau kode otorisasi dari address bar.

### Langkah 3: Tukar Kode dengan Token
```bash
python3 skills/academic-google-workspace/scripts/setup_google.py --auth-code "URL_ATAU_KODE_DISINI" --account personal
```
Token akan tersimpan secara privat di mesin lokal Anda dengan hak akses aman (`chmod 600`).

---

## 🤖 3. Penggunaan CLI Tool bagi AI Agent (`google_tool.py`)

AI Agent dapat langsung mengeksekusi perintah CLI untuk mengelola file Google:

### A. Google Sheets (Spreadsheet)
```bash
# 1. Baca data spreadsheet
python3 skills/academic-google-workspace/scripts/google_tool.py sheets get <SHEET_ID> --range "Sheet1!A1:D20"

# 2. Tambah baris baru (Append Data)
python3 skills/academic-google-workspace/scripts/google_tool.py sheets append <SHEET_ID> --values "Ahmad Fauzi,26050974001,Hadir"

# 3. Buat spreadsheet baru
python3 skills/academic-google-workspace/scripts/google_tool.py sheets create --title "Data Pengujian Praktikum Modul 2"
```

### B. Google Docs (Dokumen Makalah)
```bash
# 1. Baca isi teks Google Doc
python3 skills/academic-google-workspace/scripts/google_tool.py docs get <DOC_ID>

# 2. Buat dokumen baru dengan isi teks
python3 skills/academic-google-workspace/scripts/google_tool.py docs create --title "Draf Makalah Sistem Operasi" --text "BAB I PENDAHULUAN..."
```

### C. Google Drive (Berkas & Materi)
```bash
# 1. Cari berkas tugas atau materi kuliah
python3 skills/academic-google-workspace/scripts/google_tool.py drive search "Modul 3" --max 5

# 2. Unggah berkas laporan PDF ke Google Drive
python3 skills/academic-google-workspace/scripts/google_tool.py drive upload ~/tugas/Laporan_Final.pdf --name "Laporan_Modul_3_Wafy.pdf"
```

### D. Google Photos (Dokumentasi & Media)
```bash
# 1. Lihat daftar foto terbaru
python3 skills/academic-google-workspace/scripts/google_tool.py photos list --max 10

# 2. Lihat daftar album
python3 skills/academic-google-workspace/scripts/google_tool.py photos albums
```

### E. Google Calendar & Google Tasks
```bash
# 1. Periksa agenda perkuliahan
python3 skills/academic-google-workspace/scripts/google_tool.py calendar list --max 5

# 2. Periksa deadline tugas
python3 skills/academic-google-workspace/scripts/google_tool.py tasks list
```

---

## 🔒 4. Keamanan & Efisiensi Output (Anti-Truncation)

1. **Efisiensi Output Chat (Anti-Truncation):** Saat membaca data Google Sheets ratusan baris atau file Google Docs besar, **DILARANG** mencetak seluruh data mentah ke chat untuk mencegah token limit terlampaui (*budget exhaustion*). Sajikan ringkasan eksekutif dan tawarkan simpan ke berkas lokal jika data lengkap dibutuhkan.
2. **Kerahasiaan Lokal:** Kredensial client dan access token disimpan secara lokal di `~/.hermes/` dengan permission aman `0600`.
3. **Auto Token Refresh:** CLI script secara otomatis memperbarui access token di latar belakang saat masa aktif token habis.
