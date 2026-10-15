---
name: academic-reference-manager
description: "Kelola perpustakaan referensi Mendeley / Zotero secara otomatis: sinkronisasi metadata jurnal/buku dari DOI, unggah berkas PDF, pencarian pustaka, dan ekspor sitasi APA 7th."
tags: [unesa, academic, mendeley, reference-manager, citations, doi, pdf-sync, apa7th, research]
---

# Academic Reference Manager (Mendeley API Integration)

Skill untuk mengelola perpustakaan referensi ilmiah (Mendeley / Zotero) secara otomatis. Menghubungkan asisten AI langsung ke cloud library mahasiswa untuk mencatat sitasi, mengunggah naskah PDF artikel, mencari literatur terkait, dan memastikan kesesuaian sitasi naskah dengan standar **APA 7th Edition**.

---

## 1. Kemampuan Utama

1. **Ingest Sitasi Otomatis via Metadata / DOI:**
   Menambahkan entri pustaka baru (jurnal, prosiding, buku) ke Mendeley secara langsung dengan menyertakan judul, daftar penulis, tahun, abstrak, dan DOI.
2. **Sinkronisasi Berkas PDF ke Cloud:**
   Mengunggah berkas PDF naskah ke dokumen Mendeley yang bersangkutan (`POST /files`) sehingga dokumen langsung dapat dibaca dan diberi anotasi di Mendeley Desktop / Web.
3. **Pencarian Literatur di Pustaka:**
   Mengecek apakah suatu referensi sudah pernah tersimpan sebelum menambahkan entri baru (mencegah duplikasi).
4. **Harmonisasi Sitasi Naskah (*In-Text Citation*):**
   Memastikan nama penulis dan tahun di tubuh tulisan cocok 100% dengan database referensi (bekerja sama dengan skill `unesa-academic-standards`).

---

## 2. Alur Kerja Standar (Workflow SOP)

### Skenario A: Menyimpan Jurnal Hasil Bedah Literatur
1. Saat mahasiswa selesai membedah jurnal ilmiah menggunakan skill `smart-study-and-research`:
2. Ekstrak metadata: Judul, Penulis, Tahun, DOI, dan Abstrak.
3. Periksa apakah dokumen sudah ada di Mendeley menggunakan perintah `search`.
4. Jika belum ada, jalankan `add` untuk membuat dokumen baru dan catat `document_id`.
5. Jika berkas PDF tersedia lokal, jalankan `upload-file <document_id> <path_ke_pdf>`.
6. Laporkan status sinkronisasi ke mahasiswa: *"Artikel [Judul] berhasil ditambahkan ke pustaka Mendeley beserta berkas PDF-nya."*

### Skenario B: Audit Sitasi Makalah / Skripsi
1. Saat memeriksa naskah makalah `.docx`:
2. Cocokkan semua sitasi di tubuh paragraf (misal: *Gagne (1985)*, *Akib (2015)*) dengan daftar pustaka.
3. Sinkronkan referensi yang belum ada di Mendeley mahasiswa atau hasilkan berkas `.bib` / `.ris` pendukung.

---

## 3. Panduan Penggunaan CLI Service

Modul CLI terletak di:
`scripts/mendeley_service.py` (atau `~/.hermes/mendeley/mendeley_service.py` jika terinstal di Hermes).

### A. Cek Daftar Dokumen
```bash
python3 scripts/mendeley_service.py list --limit 20
```

### B. Tambah Dokumen Baru
```bash
python3 scripts/mendeley_service.py add \
  --title "Effectiveness of Gagné's 9 Events of Instruction in Health Professions" \
  --type journal \
  --year 2025 \
  --author "Y. Li" --author "Z. Liang" --author "X. Li" \
  --doi "10.3389/fmed.2025.1522830" \
  --abstract "Instructional design models play a crucial role in enhancing learning outcomes..."
```

### C. Unggah Berkas PDF ke Dokumen Mendeley
```bash
python3 scripts/mendeley_service.py upload-file "<DOCUMENT_ID>" "/path/to/paper.pdf"
```

### D. Cari Dokumen di Pustaka
```bash
python3 scripts/mendeley_service.py search "Gagne"
```

### E. Hapus Dokumen
```bash
python3 scripts/mendeley_service.py delete "<DOCUMENT_ID>"
```

---

## 4. Konfigurasi & Autentikasi OAuth 2.0

* **File Kredensial:** `~/.hermes/credentials/mendeley.json`
  ```json
  {
    "client_id": "12345",
    "client_secret": "abcdef...",
    "redirect_uri": "http://localhost:8080"
  }
  ```
* **File Token (Auto-Generated):** `~/.hermes/credentials/mendeley_tokens.json`
* **Inisialisasi Pertama Kali:**
  1. Dapatkan URL login:
     ```bash
     python3 scripts/mendeley_service.py auth-url
     ```
  2. Buka URL di browser, izinkan akses, lalu salin parameter `code` dari URL redirect.
  3. Tukarkan code:
     ```bash
     python3 scripts/mendeley_service.py auth-code "KODE_OTORISASI"
     ```
  *(Service CLI secara otomatis memperbarui access token jika masa berlakunya habis menggunakan refresh token).*

Panduan lengkap pembuatan aplikasi di portal developer Mendeley tersedia di:
📖 [`docs/PANDUAN_SETUP_MENDELEY_API_DAN_OAUTH.md`](../../docs/PANDUAN_SETUP_MENDELEY_API_DAN_OAUTH.md)
