---
name: lab-and-coding-practical
description: "Standar penyusunan laporan praktikum laboratorium (Informatika, Keteknikan, MIPA) dan standar penulisan kode/Jupyter Notebook."
tags: [unesa, academic, lab, praktikum, coding, jupyter, laporan-praktikum]
---

# Lab & Coding Practical Standards (Laporan Praktikum & Clean Code)

Skill panduan baku untuk menyusun laporan praktikum laboratorium (laboratorium komputer, pemrograman, elektronika, jaringan, dan sains) serta standardisasi pengerjaan tugas coding dan Jupyter Notebook (`.ipynb`).

---

## 1. Struktur Standar Laporan Praktikum (Lab Report)

Laporan praktikum resmi umumnya memiliki bobot penilaian pada **Analisis Kode** dan **Troubleshooting**, bukan sekadar menempelkan screenshot. Susun dengan bab berikut:

```text
COVER / IDENTITAS PRAKTIKAN
- Judul Modul / Percobaan
- Nama Lengkap, NIM, Kelas / Kelompok
- Program Studi & Fakultas
- Nama Asisten Laboratorium & Dosen Pengampu

I. TUJUAN PRAKTIKUM
   Merumuskan kompetensi yang ingin dicapai menggunakan kata kerja operasional (contoh: "Mampu mengimplementasikan struktur data Binary Search Tree dalam bahasa C++", "Mampu menganalisis efisiensi memori...").

II. ALAT DAN BAHAN / SPESIFIKASI ENVIRONMENT
   - Perangkat Keras: Laptop/PC (CPU, RAM, OS).
   - Perangkat Lunak: Editor (VS Code / PyCharm / CLion), Compiler/Runtime (Python 3.12 / GCC 13 / Node.js 22), DBMS (MySQL / PostgreSQL / SQLite).
   - Library Tambahan: numpy 2.1, pandas 2.2, matplotlib 3.9, dll.

III. DASAR TEORI
   Ringkasan konsep fundamental yang relevan dengan modul (1–2 halaman). Berisi rumus matematis, diagram arsitektur, atau alur algoritma.

IV. LANGKAH KERJA / PROSEDUR
   Tahapan sistematis yang dilakukan selama percobaan di laboratorium.

V. HASIL DAN ANALISIS PROGRAM
   Bagian paling krusial! Memuat:
   1. Cuplikan Source Code (Clean Code)
   2. Screenshot Output Terminal / GUI
   3. Analisis Logika Kode Per-Blok (Penjelasan alur logika fungsi, variabel, loop, dan kompleksitas waktu/ruang)

VI. TUGAS / SOAL PENGEMBANGAN (POST-TEST)
   Jawaban studi kasus atau variasi soal yang diberikan asisten laboratorium.

VII. KESIMPULAN & TROUBLESHOOTING
   - Kesimpulan: Jawaban ringkas atas tujuan praktikum berdasarkan data hasil uji.
   - Troubleshooting Log: Daftar error/bug yang ditemui saat praktikum (misal: *Segmentation Fault*, *IndexError*, *Port Conflict*) beserta solusi penyelesaiannya.

DAFTAR PUSTAKA
```

---

## 2. Standar Analisis Source Code (Anti-Copypaste)

Saat menjelaskan kode di laporan praktikum, gunakan pola analisis blok terstruktur:

```markdown
### Percobaan 1: Implementasi Binary Search

```python
def binary_search(arr: list[int], target: int) -> int:
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid  # Elemen ditemukan
        elif arr[mid] < target:
            left = mid + 1  # Cari di paruh kanan
        else:
            right = mid - 1  # Cari di paruh kiri
            
    return -1  # Elemen tidak ditemukan
```

#### Analisis Logika Program:
1. **Inisialisasi Pointer (Baris 2-3):** Pointer `left` diatur pada indeks 0 dan `right` pada indeks akhir `len(arr) - 1`.
2. **Looping Kondisional (Baris 5):** Kondisi `left <= right` memastikan pencarian tetap valid selama ruang pencarian belum habis.
3. **Titik Tengah & Pembagian Ruang (Baris 6-12):** Variabel `mid` dihitung menggunakan operasi *integer division* `//` untuk menghindari nilai float. Pada setiap iterasi, jika `arr[mid] != target`, ruang pencarian dipotong setengah, sehingga algoritma mencapai efisiensi waktu logarithmic $\mathcal{O}(\log n)$.
```

---

## 3. Standar Kebersihan Jupyter Notebook (`.ipynb`)

Bagi praktikum Data Science, AI, atau Statistika yang mengumpulkan berkas `.ipynb`:

1. **Urutan Eksekusi Harus Linear `[1] s.d. [N]`:**
   * Sebelum mengumpulkan berkas, wajib jalankan **`Restart Kernel & Run All Cells`**.
   * Dilarang mengumpulkan notebook dengan urutan lompat-lompat (misal `[14]`, lalu `[2]`, lalu `[40]`) karena menandakan state variabel tidak konsisten.
2. **Struktur Markdown Cell Sebagai Navigasi:**
   * Setiap nomor percobaan wajib diawali Markdown Header `## Percobaan X: [Nama Modul]`.
   * Penjelasan interpretasi grafik/tabel diletakkan tepat di bawah output cell terkait.
3. **Bebas dari Warning/Error Menumpuk:**
   * Bersihkan output stack trace error panjang yang tidak perlu.
   * Supress warning library yang tidak relevan dengan `warnings.filterwarnings('ignore')` jika output mengganggu kerapian laporan.
