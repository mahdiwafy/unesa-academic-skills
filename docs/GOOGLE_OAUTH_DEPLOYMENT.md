# 🔐 Panduan Arsitektur Google Cloud & OAuth untuk Distribusi Mahasiswa

Dokumen ini menjelaskan strategi menghubungkan Google Workspace (Google Calendar, Google Tasks, Google Forms, Drive) untuk asisten AI mahasiswa/pelanggan secara **aman, legal, stabil, dan sesuai kebijakan Google Identity/OAuth**.

---

## 1. Jawaban Langsung atas Pertanyaan Kunci

### A. Apakah bisa dibuatkan skill jadwal akademik dan hidup?
**Bisa dan sangat direkomendasikan.** Skill `academic-life-schedule` membedakan agenda waktu (`Google Calendar`) dan aksi/tenggat (`Google Tasks`), mendeteksi perubahan jam/ruang secara otomatis, mencegah duplikasi jadwal (*upsert pattern*), serta memperhitungkan waktu perjalanan dan persiapan.

### B. Apakah bagus memakai satu Google Cloud Console milik kita untuk semua orang?
* **Untuk tahap teman / pilot (<= 100 orang):** Bisa memakai 1 Google Cloud Project dalam status **Testing** dengan mendaftarkan email masing-masing sebagai **Test Users**.
* **Untuk produk komersial / publik luas (> 100 orang):** **TIDAK BISA** hanya dibiarkan apa adanya. Google mewajibkan verifikasi aplikasi resmi (*App Verification*) untuk scope sensitif seperti Calendar dan Tasks.

### C. Apakah memakai project milik kita langsung otomatis dianggap "komersil"?
**Bukan otomatis karena kepemilikan project, melainkan karena scope data, basis pengguna, dan status publikasi.**
1. **Status Testing (Khusus Internal/Teman Dekat):**
   * Gratis, tidak butuh verifikasi domain, tapi dibatasi maksimal 100 email terdaftar (*Test Users*).
   * Token refresh memiliki batas waktu 7 hari sehingga pengguna harus login ulang secara periodik.
2. **Status In Production / Unverified (Komersil Awal):**
   * Membuka akses ke publik tetapi dibatasi kuota 100 user dan menampilkan layar peringatan berbahaya (*"Google hasn't verified this app"*).
3. **Status In Production (Verified App):**
   * Wajib memiliki domain ber-HTTPS, halaman Landing Page publik, Privacy Policy, Terms of Service, serta mengirim video demo penggunaan data ke Google Trust & Safety.
   * Tidak ada batasan 100 user dan token refresh tidak kedaluwarsa tiap 7 hari.

---

## 2. Pilihan Model Deployment Google OAuth

| Aspek | Opsi A: Self-Host OAuth (Tiap User Bikin Project) | Opsi B: Centralized Pilot (1 Project Status Testing) | Opsi C: Centralized Commercial (1 Project Verified) |
| :--- | :--- | :--- | :--- |
| **Cocok untuk** | Mahasiswa IT / Tech-Savvy / Open-Source | Teman sekelas / Teman dekat (< 50 orang) | Jasa/Layanan Komersial Berbayar Langganan |
| **Kemudahan User** | Butuh 5 menit setup Cloud Console | User tinggal klik link login & copy code | User cukup klik tombol "Sign in with Google" |
| **Batasan User** | Unlimited (Project milik masing-masing) | Maksimal 100 user (wajib input email) | Unlimited |
| **Masa Berlaku Token** | Permanen (bila diset ke Production Unverified) | 7 Hari (otomatis expired karena status Testing) | Permanen (selama tidak di-revoke user) |
| **Biaya & Legalitas** | 100% Gratis & Mandiri | Gratis | Gratis registrasi Google, butuh domain terverifikasi |

---

## 3. Scope Minimum (Least-Privilege Standard)

Jangan meminta akses penuh ke seluruh akun Google pengguna jika hanya ingin mengelola jadwal dan tugas:

```text
# 📅 Kalender: Buat & perbarui event di kalender pengguna
https://www.googleapis.com/auth/calendar.events.owned

# 📝 Tugas: Buat & centang deadline penugasan
https://www.googleapis.com/auth/tasks

# ❌ HINDARI SCOPE INVASIF (Kecuali Fitur Tersebut Benar-Benar Disediakan):
# - https://mail.google.com/ (Akses penuh baca/tulis email Gmail)
# - https://www.googleapis.com/auth/drive (Akses seluruh file Google Drive)
```

---

## 4. Keamanan & Sanitasi Kredensial

1. **Dilarang Komit Kredensial ke Git:**
   * Jangan pernah menyimpan file `client_secret.json`, `google_token.json`, atau `.env` berisi token ke dalam repositori publik.
2. **Isolasi Data Antar-Pengguna:**
   * Setiap pelanggan harus memiliki file token tersendiri yang terenkripsi dan terikat ke session mereka.
   * Tidak boleh ada pengguna yang bisa membaca atau mengedit jadwal/tugas pengguna lain.
3. **Hak Pencabutan Akses:**
   * Pengguna harus selalu diberi tahu bahwa mereka dapat mencabut izin aplikasi kapan pun melalui [https://myaccount.google.com/permissions](https://myaccount.google.com/permissions).
