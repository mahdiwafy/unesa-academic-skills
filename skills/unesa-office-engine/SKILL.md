---
name: unesa-office-engine
description: "Manipulasi dan pembuatan dokumen Office (.docx, .xlsx, .pptx) di laptop/PC tanpa perlu install Microsoft Office berat via officecli & script automasi."
tags: [unesa, office, docx, xlsx, pptx, word, excel, powerpoint, officecli, laptop]
---

# UNESA Office Engine (Word, Excel & PowerPoint di Laptop)

Skill untuk membuat, mengedit, memformat, dan memvisualisasikan dokumen Microsoft Office (**Word `.docx`**, **Excel `.xlsx`**, **PowerPoint `.pptx`**) secara instan di laptop/PC mahasiswa (Windows, macOS, Linux) tanpa ketergantungan lisensi Microsoft Office berat, menggunakan **`officecli`** dan generator script terintegrasi.

---

## 1. Setup 1-Klik di Laptop Mahasiswa

`officecli` adalah single binary super-ringan (tanpa perlu install MS Office berbayar):

### A. Laptop Windows (PowerShell)
Buka PowerShell dan jalankan:
```powershell
irm https://d.officecli.ai/install.ps1 | iex
```

### B. Laptop macOS / Linux
Buka Terminal dan jalankan:
```bash
curl -fsSL https://d.officecli.ai/install.sh | bash
```

Verifikasi instalasi:
```bash
officecli --version
```

---

## 2. Fitur Unggulan untuk Tugas Kuliah di Laptop

### A. Live Preview di Browser Laptop (`officecli watch`)
Mahasiswa bisa melihat hasil dokumen yang dibuat AI secara *real-time* di browser laptop:
```bash
# Buka preview live dokumen di browser lokal
officecli watch makalah_sistem_operasi.docx
# Buka http://localhost:26315 di Chrome/Edge
```
*Setiap kali file diperbarui atau diedit oleh AI, browser akan otomatis me-refresh tampilan tanpa perlu buka-tutup Microsoft Word.*

---

## 3. Kompilasi Perintah Cepat (Cheat-Sheet Tugas)

### 📄 1. Microsoft Word (.docx)
* **Bikin Dokumen Baru:**
  ```bash
  officecli create tugas_makalah.docx
  officecli add tugas_makalah.docx /body --type paragraph --prop text="BAB I PENDAHULUAN" --prop style=Heading1
  officecli add tugas_makalah.docx /body --type paragraph --prop text="Latar belakang permasalahan..."
  ```
* **Find & Replace Massal (Ganti Istilah/Nama):**
  ```bash
  officecli set tugas_makalah.docx / --find "istilah_lama" --replace "istilah_baru"
  ```
* **Periksa Kerusakan / Masalah Format:**
  ```bash
  officecli view tugas_makalah.docx issues
  ```

---

### 📊 2. Microsoft Excel (.xlsx)
* **Bikin Spreadsheet Pengolahan Data Praktikum:**
  ```bash
  officecli create data_praktikum.xlsx
  officecli set data_praktikum.xlsx /Sheet1/A1 --prop value="No" --prop bold=true
  officecli set data_praktikum.xlsx /Sheet1/B1 --prop value="Nilai Uji (ms)" --prop bold=true
  officecli set data_praktikum.xlsx /Sheet1/A2 --prop value=1
  officecli set data_praktikum.xlsx /Sheet1/B2 --prop value=14.5
  ```
* **Bikin Pivot Table Otomatis:**
  ```bash
  officecli add data_praktikum.xlsx /Sheet1 --type pivottable \
    --prop source="Sheet1!A1:E100" --prop rows=Kategori \
    --prop values="Nilai:average"
  ```

---

### 📽️ 3. Microsoft PowerPoint (.pptx)
* **Bikin Slide Presentasi 10 Slide Bersih:**
  ```bash
  officecli create presentasi_kelompok.pptx
  # Slide 1: Cover
  officecli add presentasi_kelompok.pptx / --type slide --prop title="Arsitektur Jaringan Komputer" --prop background="0055A5"
  officecli add presentasi_kelompok.pptx '/slide[1]' --type shape --prop text="Disusun oleh: Kelompok 4 - PTI UNESA" \
    --prop x=2cm --prop y=5cm --prop font=Arial --prop size=20 --prop color=FFFFFF
  ```
* **Lihat Struktur Slide:**
  ```bash
  officecli view presentasi_kelompok.pptx outline
  ```

---

## 4. Troubleshooting Dokumen di Laptop

1. **File Terkunci (File in use):**
   * Pastikan file `.docx`/`.xlsx`/`.pptx` ditutup terlebih dahulu dari aplikasi MS Word / WPS Office sebelum diedit oleh perintah CLI.
2. **Margin Tidak Sesuai di Word:**
   * Gunakan `python skills/unesa-academic-standards/scripts/generate_docx.py` atau set dokumen defaults lewat `officecli set doc.docx / --prop docDefaults.font="Times New Roman"`.
