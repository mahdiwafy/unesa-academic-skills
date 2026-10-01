---
name: academic-presentation-mastery
description: "Arsitektur pembuatan slide presentasi kuliah (PowerPoint/Marp/Canva) 8-12 slide efektif dilengkapi Speaker Notes (naskah bicara)."
tags: [unesa, academic, presentation, pptx, slides, speaker-notes, marp]
---

# Academic Presentation Mastery (Slide Kuliah & Naskah Presentasi)

Skill untuk merancang materi presentasi perkuliahan berdurasi 10–15 menit yang profesional, terstruktur, tajam secara visual, dan dilengkapi panduan narasi bicara (*Speaker Notes*) bagi presenter.

---

## 1. Arsitektur Struktur 10-Slide Presentasi Kuliah

Gunakan formula 10 slide ideal untuk presentasi tugas kelompok / individu:

| No. Slide | Nama Bagian | Fokus Konten | Target Durasi Bicara |
| :--- | :--- | :--- | :--- |
| **Slide 1** | **Title / Hook** | Judul menarik, Mata Kuliah, Dosen Pengampu, Nama Anggota Kelompok & NIM. | 30 detik |
| **Slide 2** | **Problem Statement** | Latar belakang masalah & urgensi: "Kenapa topik ini penting untuk kita kaji?" | 60 detik |
| **Slide 3** | **Objectives / Scope** | Rumusan masalah dan batasan pembahasan yang akan diuraikan. | 45 detik |
| **Slide 4** | **Core Theory (Part 1)** | Konsep fundamental / definisi operasional / arsitektur dasar. | 90 detik |
| **Slide 5** | **Core Theory (Part 2)** | Mekanisme kerja, alur proses, atau perbandingan metode (Framework). | 90 detik |
| **Slide 6** | **Deep Dive / Analysis** | Analisis kritis atau data pendukung (grafik/tabel perbandingan). | 90 detik |
| **Slide 7** | **Case Study / Implementation** | Contoh penerapan nyata di lapangan / studi kasus di Indonesia / demo. | 90 detik |
| **Slide 8** | **Challenges & Solutions** | Hambatan/kendala yang muncul beserta alternatif solusi penanganannya. | 60 detik |
| **Slide 9** | **Conclusion & Takeaways** | 3 kesimpulan utama (Key Takeaways) yang wajib diingat audiens. | 60 detik |
| **Slide 10** | **Q&A & References** | Ajakan diskusi tanya jawab dan daftar 2-3 referensi utama (DOI/Jurnal). | 30 detik |

---

## 2. Prinsip Anti-Pusing Desain Slide (Visual Standards)

1. **Prinsip "1 Slide = 1 Gagasan Utama":**
   * Jangan menumpuk 3 konsep berbeda dalam 1 slide.
   * Judul slide harus berupa *Action Headline* (Contoh: *"Peningkatan Efisiensi dengan Metode X"*, bukan sekadar *"Metode X"*).
2. **Aturan 6 x 6 (Anti-Wall of Text):**
   * Maksimal 4–6 baris bullet point per slide.
   * Maksimal 6–8 kata per baris.
   * **DILARANG** meng-copy-paste paragraf makalah utuh ke dalam slide. Slide adalah *visual anchor*, narasinya diucapkan oleh presenter.
3. **Hierarki Ukuran Font (Legibility 10 Meter):**
   * Judul Slide: **28 – 36 pt (Bold)**
   * Sub-heading / Poin Utama: **20 – 24 pt (Semibold)**
   * Keterangan Tambahan: **16 – 18 pt**
   * *Hindari font dekoratif/handwriting. Gunakan font modern bersih: Inter, Roboto, Poppins, Arial, Montserrat.*
4. **Kontras & Palet Warna:**
   * Latar belakang terang (Putih/Off-white) dengan teks gelap (Hitam/Abu-abu tua `#1e293b`), atau sebaliknya untuk dark mode.
   * Gunakan maksimal 2 warna aksen (misal: Biru UNESA `#0055a5` dan Kuning Emas).

---

## 3. Format Output Dual-Output: Slide + Speaker Notes

Setiap kali diminta membuat presentasi, sajikan dalam format berikut:

```markdown
### SLIDE 2: Problem Statement - Tantangan Penjadwalan Akademik
**Visual Slide:**
* Judul: "Tantangan Penjadwalan: Efisiensi vs Konflik Ruang"
* 3 Poin Kunci:
  - Fluktuasi ketersediaan ruang kuliah luring pasca-pandemi
  - Beban kerja manual PJ MK dalam sinkronisasi jadwal dosen
  - Keterlambatan broadcast informasi ke mahasiswa (>30 menit)
* Visual: Diagram alur bottleneck penjadwalan konvensional

---
🎙️ **Speaker Notes (Naskah Bicara):**
"Selamat pagi rekan-rekan dan Bapak Dosen. Sebelum kita masuk ke solusi teknis, mari kita lihat realita yang sering kita alami setiap awal semester. Masalah penjadwalan kuliah sering kali memakan waktu bukan karena rumitnya mata kuliah, tetapi karena koordinasi ruang dan waktu yang masih dilakukan secara manual. Hal ini menciptakan bottleneck yang mengakibatkan informasi sering terlambat sampai ke mahasiswa. Di slide berikutnya, kita akan bedah bagaimana sistem otomatisasi dapat memangkas waktu tunggu ini hingga 80%."
```

---

## 4. Format Marp (Markdown to Slide Deck)

Jika membuat presentasi berbasis kode, gunakan format Marp:

```markdown
---
marp: true
theme: default
paginate: true
header: 'Mata Kuliah: Sistem Informasi | UNESA 2026'
footer: 'Kelompok 3 - S1 PTI'
---

# Optimalisasi Sistem Antrean Perkuliahan
### Studi Kasus: Implementasi Algoritma FCFS pada SIAKADU
**Disusun oleh:**
* Ahmad Fauzi (26050974001)
* Budi Santoso (26050974002)

---

## Urgensi Permasalahan
- Lonjakan traffic server saat masa KRS-an (hingga 10.000 req/sec)
- Waktu tunggu respon halaman mencapai >15 detik
- Kebutuhan alokasi antrean dinamis berbasis prioritas semester

---

## Solusi & Arsitektur
1. **Load Balancing:** Distribusi beban ke worker nodes
2. **In-Memory Caching:** Reduksi hit langsung ke database SQL
3. **Graceful Queueing:** Notifikasi estimasi waktu antre pengguna
```
