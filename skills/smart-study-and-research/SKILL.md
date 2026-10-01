---
name: smart-study-and-research
description: "Framework bedah jurnal ilmiah (SINTA/Scopus/IEEE), sintesis literatur, serta generator study guide & bank soal persiapan UTS/UAS."
tags: [unesa, academic, research, bedah-jurnal, sinta, scopus, study-guide, uts-uas]
---

# Smart Study & Research Framework (Bedah Jurnal & Persiapan Ujian)

Skill untuk membedah artikel ilmiah/jurnal bereputasi (SINTA 1–4, Scopus Q1–Q4, IEEE, ScienceDirect) secara cepat dan terstruktur, menyusun sintesis literatur, serta menghasilkan ringkasan materi belajar dan bank soal evaluasi untuk persiapan UTS/UAS.

---

## 1. Matrix Ekstraksi Jurnal 5 Menit (Literature Analysis)

Ketika diminta menganalisis artikel ilmiah atau menyusun tugas telaah jurnal, gunakan template analisis komprehensif berikut:

```markdown
# TELAAH KRITIS ARTIKEL ILMIAH

### 1. Identitas Dokumen
* **Judul Artikel:** [Judul Lengkap]
* **Penulis:** [Nama Semua Penulis]
* **Nama Jurnal / Konferensi:** [Nama Jurnal], Vol. X, No. Y, Tahun [Tahun], Halaman xx-yy
* **Akreditasi / Reputasi:** [SINTA 2 / Scopus Q2 / dll.]
* **DOI / Link:** [https://doi.org/10.xxxx/...]

---

### 2. Intisari Penelitian (Core Research Breakdown)
* **Latar Belakang & Urgensi:** Apa fenomena riil atau permasalahan kritis yang melatarbelakangi penelitian ini?
* **Research Gap:** Apa kekurangan atau celah dari penelitian-penelitian terdahulu yang coba diselesaikan oleh penulis?
* **Rumusan / Pertanyaan Penelitian:** Pertanyaan kunci apa yang ingin dijawab?

---

### 3. Metodologi & Desain Eksperimen
* **Pendekatan:** Kuantitatif / Kualitatif / R&D / Eksperimen / Systematic Literature Review.
* **Subjek / Sampel / Dataset:** Jumlah sampel, karakteristik responden, atau dataset yang digunakan (misal: 5.000 data transaksi).
* **Teknik Pengumpulan Data:** Observasi, kuesioner skala Likert, API scraping, uji laboratorium.
* **Metode Analisis / Algoritma:** Model statistik (SEM-PLS, ANOVA) atau algoritma (Random Forest, CNN, Dijkstra).
* **Metrik Evaluasi:** Akurasi, Precision, Recall, F1-Score, RMSE, $R^2$, atau uji signifikansi p-value.

---

### 4. Temuan Utama & Pembahasan (Findings)
* **Hasil Kunci:** Temuan empiris utama yang diperoleh beserta data numerik/faktual pendukung.
* **Kontribusi / Novelty:** Kebaruan yang ditawarkan oleh penelitian ini dibanding studi sebelumnya.

---

### 5. Evaluasi Kritis & Peluang Riset Lanjutan
* **Kelebihan Studi:** Kekuatan metodologi, validitas data, atau kejelasan pembahasan.
* **Kelemahan / Limitasi:** Batasan ruang lingkup, ukuran sampel yang terbatas, atau asumsi yang belum teruji.
* **Peluang Penelitian Lanjutan (Future Work):** Gagasan ide skripsi/tugas yang dapat dikembangkan dari kekurangan penelitian ini.
```

---

## 2. Generator Study Guide & Persiapan UTS / UAS

Ketika diminta membuat ringkasan materi belajar untuk persiapan ujian:

### A. Format Rangkuman Konsep (Study Guide)
* **Definisi Inti:** Ringkasan dalam 1–2 kalimat tanpa jargon berlebih.
* **Analogika Sederhana:** Perumpamaan dalam kehidupan sehari-hari untuk konsep yang rumit.
* **Diagram Logika / Alur:** Langkah-langkah mekanisme dalam bentuk diagram teks / markdown list.
* **Formula / Sintaks Kunci:** Rumus matematika atau sintaks kode terpenting.

### B. Format Bank Soal Evaluasi Mandiri (Tingkat C3–C5 Bloom)
Hasilkan soal bertipe analisis dan pemecahan kasus, bukan sekadar hafalan definisi:

```markdown
### Latihan Soal Kasus:
**Soal:** 
Sebuah sistem database perpustakaan mengalami *lock contention* saat ratusan mahasiswa mengakses katalog secara bersamaan pada pekan pertama perkuliahan. Jelaskan mengapa fenomena ini terjadi dan berikan 2 strategi optimasi level arsitektur untuk mengatasi lonjakan beban tersebut!

**Kunci Jawaban & Pembahasan Mendalam:**
1. **Analisis Penyebab:** Terjadinya *contention* disebabkan oleh...
2. **Solusi 1 (Read-Replicas & Caching):** Mengimplementasikan Redis caching layer untuk queries data katalog yang bersifat *read-heavy*...
3. **Solusi 2 (Connection Pooling):** Mengonfigurasi max connection pool dan indexing pada kolom pencarian utama...
```

---

## 3. Flashcard Generator (Spaced Repetition)

Gunakan format kompatibel Anki / Quizlet:

```text
Q: Apa perbedaan mendasar antara Proses (Process) dan Utas (Thread) dalam Sistem Operasi?
A: Proses adalah program yang sedang dieksekusi dengan ruang alamat memori mandiri (isolated memory space), sedangkan Thread adalah unit eksekusi terkecil di dalam proses yang berbagi ruang memori (shared memory) yang sama dengan thread lainnya dalam proses tersebut.

Q: Mengapa indeks B-Tree lebih disukai daripada Hash Index pada kolom database relasional?
A: Karena B-Tree mendukung pencarian rentang nilai (range queries, >, <, BETWEEN) dan pengurutan (ORDER BY) secara efisien, sedangkan Hash Index hanya mendukung pencarian nilai pasti (exact match, =).
```
