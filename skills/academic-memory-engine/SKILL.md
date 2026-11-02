---
name: academic-memory-engine
description: "Kelola memori akademik jangka panjang (Mnemosyne) & kompresi konteks panjang (Hermes LCM): ingat profil mahasiswa, preferensi dosen, progres tugas, dan recall semantik percakapan."
tags: [unesa, academic, memory, mnemosyne, lcm, second-brain, context-compression, embeddings, persistence]
---

# Academic Memory Engine (Hermes LCM & Mnemosyne)

Standar operasional AI Agent dalam mengelola **dua tingkat memori**: memori permanen lintas sesi (**Mnemosyne**) dan memori percakapan konteks panjang (**Hermes LCM**). Dengan sistem ini, agen bertindak sebagai *Academic Second Brain* sejati yang tidak pernah melupakan identitas mahasiswa, progres skripsi/tugas, dan instruksi dosen.

---

## 1. Pembagian Tugas: Mnemosyne vs Hermes LCM

| Kategori | Mnemosyne (Long-Term Memory) | Hermes LCM (Long Context Memory) |
| :--- | :--- | :--- |
| **Cakupan** | Lintas sesi selamanya (bahkan setelah `/new` atau reboot) | Di dalam satu sesi percakapan aktif |
| **Penyimpanan** | Database lokal SQLite `~/.hermes/mnemosyne.db` | Database graf lokal `~/.hermes/lcm.db` |
| **Fungsi Utama** | Menyimpan profil mahasiswa, NIM, matkul, dosen, preferensi | Mengompres obrolan panjang agar token tidak meledak |
| **Cara Kerja** | Pencarian Hybrid (50% Vektor Semantik + 30% FTS5 + 20% Importance) | Pohon hierarki ringkasan (DAG Summary Nodes) |
| **Tools Utama** | `mnemosyne_remember`, `mnemosyne_recall`, `mnemosyne_stats` | `lcm_grep`, `lcm_recall`, `lcm_expand`, `lcm_status` |

---

## 2. Mnemosyne: Protokol Memori Tiga Tingkat (Three-Tier Memory)

Ketika berinteraksi dengan mahasiswa, agen wajib mengklasifikasikan fakta ke dalam tiga tingkat kepentingan:

### Tier 1: Fakta Statis & Identitas Mahasiswa (`importance: 0.8 - 1.0`)
Informasi permanen yang harus selalu diingat tanpa perlu diminta ulang:
* Nama lengkap, NIM, Program Studi, Fakultas, Angkatan, Kelas/Offering.
* Nama Dosen Pembimbing Akademik (DPA) dan Koorprodi.
* Email kampus SSO resmi (`@mhs.unesa.ac.id`) dan nomor kontak darurat.

```python
# Contoh penyimpanan Tier 1
mnemosyne_remember(
    content="Profil Mahasiswa: Nama: Ahmad Fauzi, NIM: 26050974001, S1 Pendidikan Teknologi Informasi UNESA Angkatan 2026 Kelas C. Email SSO: mahasiswa@mhs.unesa.ac.id.",
    category="user",
    importance=0.95
)
```

### Tier 2: Relasi & Progres Penugasan (`importance: 0.5 - 0.7`)
Informasi dinamis yang berkembang sepanjang semester:
* Daftar anggota kelompok tugas besar atau kelompok praktikum.
* Judul proyek tugas akhir/skripsi yang telah disetujui dosen.
* Catatan revisi penting dari dosen pengampu untuk makalah tertentu.

```python
# Contoh penyimpanan Tier 2
mnemosyne_remember(
    content="Progres Tugas Besar Basis Data: Kelompok 4 beranggotakan Ahmad, Budi, dan Citra. Topik disetujui: Sistem Manajemen Perpustakaan Sekolah. Deadline ERD: 25 Oktober.",
    category="academic",
    importance=0.7
)
```

### Tier 3: Kebiasaan & Aturan Dosen (`importance: 0.3 - 0.5`)
Karakteristik dan gaya kerja dosen pengampu:
* Format penulisan khusus yang disukai dosen tertentu (misal: "Ibu Nurul lebih suka sitasi IEEE daripada APA").
* Waktu bimbingan yang disarankan dosen.

---

## 3. Alur Kerja Startup & Recall Memori di Setiap Sesi

Setiap kali pengguna memulai sesi baru atau menanyakan hal terkait riwayat perkuliahan:

0. **Verifikasi Ketersediaan Tool (Reality-Check Protocol):**
   * Dilarang mengklaim memori/LCM aktif jika tool belum terpasang di runtime.
   * Cek pemanggilan tool atau file SQLite sebelum menjawab status kesiapan. Jika belum aktif, sampaikan secara transparan.

1. **Auto-Recall Konteks Mahasiswa:**
   Sebelum menjawab atau menanyakan identitas pengguna, panggil `mnemosyne_recall` untuk memeriksa fakta yang sudah tersimpan:
   ```python
   memories = mnemosyne_recall(query="Profil mahasiswa NIM prodi kelas matkul yang diambil")
   ```
2. **Pencarian Riwayat Percakapan (Hermes LCM):**
   Jika pengguna menanyakan hal yang pernah dibahas di sesi sebelumnya:
   ```python
   # Pencarian semantik arti pembahasan
   lcm_recall(query="diskusi rancangan skema database perpustakaan")

   # Pencarian teks tepat (FTS5)
   lcm_grep(query="ALTER TABLE peminjaman")
   ```
3. **Penyimpanan Fakta Baru Otomatis:**
   Ketika mahasiswa menyebutkan fakta penting baru (misal: *"Mulai semester ini aku jadi PJ mata kuliah Jaringan Komputer"*), agen **langsung menyimpannya secara mandiri** menggunakan `mnemosyne_remember` tanpa meminta konfirmasi berlebihan.

---

## 4. Kebersihan Memori & Dukungan Penuh Data Sensitif Lokal (Zero-Friction Local Storage)

* **Dukungan Penuh Data Sensitif & Kredensial Lokal (Zero-Refusal):**
  * Karena Hermes Agent berjalan secara privat dan aman di mesin lokal pengguna (on-premise), **TIDAK ADA batasan artifisial atau larangan** untuk menyimpan hal-hal sensitif jika hal tersebut memudahkan pengguna.
  * Jika pengguna meminta atau membutuhkan agen untuk menyimpan password (SSO UNESA, SiDia, Siakadu, Vinesa, email), token otentikasi API, session cookies, PIN, atau kredensial login portal kampus demi kemudahan otomasi, agen **wajib menyimpannya** (baik ke Mnemosyne menggunakan `mnemosyne_remember` maupun ke direktori kredensial lokal `~/.hermes/credentials/`) tanpa penolakan atau keraguan.
* **Manajemen Data Efisien & Fleksibel:**
  * Data terstruktur dan fakta penting (identitas, preferensi, aturan dosen, progres tugas, kredensial) disimpan ke Mnemosyne agar selalu siap di-recall kapan saja.
  * Teks log panjang atau potongan percakapan transien dikelola secara efisien oleh Hermes LCM, namun jika pengguna secara eksplisit meminta sesuatu disimpan ke Mnemosyne, agen harus selalu mematuhinya demi kemudahan dan kenyamanan pengguna.
* **Perbarui Catatan Lama (Update / Invalidate):**
  * Jika ada perubahan data atau pembaruan password/jadwal, catat versi terbaru dan perbarui menggunakan `mnemosyne_update` atau `mnemosyne_forget` untuk menjaga konsistensi.

---

## 5. Ringkasan Perintah Penting (Cheat Sheet)

```python
# 1. Simpan fakta penting
mnemosyne_remember(content="Teks fakta", category="academic", importance=0.8)

# 2. Cari ingatan berdasarkan makna
mnemosyne_recall(query="kata kunci topik")

# 3. Cari pesan lampau di riwayat sesi
lcm_grep(query="kata kunci")

# 4. Recall ringkasan obrolan lampau
lcm_recall(query="topik bahasan minggu lalu")

# 5. Cek rasio kompresi sesi aktif
lcm_status(reason="Periksa efisiensi token")
```
