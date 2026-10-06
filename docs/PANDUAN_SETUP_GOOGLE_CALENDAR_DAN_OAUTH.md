# 📖 Panduan Lengkap Integrasi Google Calendar & Tasks (Neo Agent)

Panduan ini berisi langkah-langkah praktis:
1. **Untuk Teman / Pelanggan:** Cara menghubungkan akun Google ke asisten AI dalam 1 menit.
2. **Untuk Developer / Owner (Wafy):** Cara mengajukan *Official Google App Verification* (Gratis) saat kuota mendekati 100 pengguna.
3. **Untuk Mahasiswa IT (Opsi Mandiri):** Cara membuat Google Cloud Console Project sendiri dari nol.

---

## 🚀 Bagian 1: Cara Pengguna / Teman Login Google (1 Menit)

Jika menggunakan project Google Cloud terpusat dari **Neo Agent**:

### Langkah 1: Minta Tautan Login ke Agen AI
Ketik di chat agen:
```text
"Bantu hubungkan akun Google Calendar dan Google Tasks saya."
```
Atau jalankan perintah CLI:
```bash
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url
```
Agen akan memberikan sebuah tautan (URL) login Google.

### Langkah 2: Buka URL di Browser & Klik Izin
1. Buka URL tersebut di browser (Chrome / Edge).
2. Pilih akun Google yang ingin dihubungkan (misal akun email kampus atau pribadi).
3. **Layar Peringatan "Google hasn't verified this app" (Wajar):**
   * Klik tombol kecil **"Advanced"** (atau **"Lanjutan"** di pojok kiri bawah).
   * Klik **"Go to Neo Agent (unsafe)"** / **"Buka Neo Agent (tidak aman)"**.
   *(Catatan: Ini aman karena asisten AI berjalan di mesin Anda sendiri).*
4. Centang izin **Google Calendar** dan **Google Tasks** -> Klik **"Continue"** / **"Lanjutkan"**.

### Langkah 3: Salin URL Redirect ke Chat / Terminal
1. Setelah klik izinkan, browser akan menampilkan halaman kosong bertuliskan `http://localhost:1/?code=4/0A...` (ini normal).
2. **Salin seluruh teks URL di address bar browser**.
3. Paste URL tersebut ke chat agen atau terminal:
   ```bash
   python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "URL_YANG_DISALIN"
   ```
4. **Selesai!** Token otomatis tersimpan secara permanen di perangkat Anda. Jadwal kuliah dan tugas akan otomatis tersinkronisasi.

---

## 🛡️ Bagian 2: Panduan Wafy untuk Google App Verification (Menghapus Limit 100 User)

Ketika jumlah teman/pelanggan yang menggunakan layanan sudah mencapai 60–80 orang, lakukan verifikasi resmi ke Google (100% Gratis) agar peringatan *"unverified app"* hilang dan batas 100 user dicabut menjadi *Unlimited*.

### Persyaratan Sebelum Submit:
1. **Domain Terverifikasi:** Domain `mahdiwafy.my.id` sudah terhubung di Google Search Console.
2. **Halaman Publik Aktif:**
   * Homepage: `https://mahdiwafy.my.id`
   * Privacy Policy: `https://mahdiwafy.my.id/privacy` (menjelaskan data kalender hanya digunakan untuk penjadwalan pengguna).
   * Terms of Service: `https://mahdiwafy.my.id/terms`
3. **Video Demo (1–2 Menit di YouTube Unlisted):**
   * Rekam layar alur login OAuth (dalam bahasa Inggris / teks keterangan):
     1. Menampilkan layar browser dengan Client ID terlihat di address bar.
     2. Menampilkan layar persetujuan izin Calendar & Tasks.
     3. Menunjukkan AI berhasil membuat satu jadwal di Google Calendar / Google Tasks.
   * Upload ke YouTube dengan privasi **Unlisted** (Tidak Publik).

### Langkah Pengajuan di Google Cloud Console:
1. Buka [Google Cloud Console](https://console.cloud.google.com/apis/credentials/consent).
2. Pilih project **`leo-project-498200`** (atau nama project aktif).
3. Buka menu **OAuth consent screen** -> Klik tombol **"Submit for Verification"** (atau **"Verify App"**).
4. Isi data yang diminta:
   * **App Name:** Neo Agent
   * **User Support Email & Developer Contact:** `wafy.081107@gmail.com`
   * **Scope Justification:**
     * `calendar.events.owned` / `calendar`: *"Digunakan untuk membuat dan memperbarui jadwal kuliah, kelas pengganti, dan rapat pengguna secara otomatis."*
     * `tasks`: *"Digunakan untuk mencatat deadline tugas kuliah dan checklist praktikum pengguna."*
   * **YouTube Video Link:** Tempelkan link video YouTube Unlisted yang sudah dibuat.
5. Klik **Submit**.
6. **Waktu Review:** Tim Google Trust & Safety akan meninjau dalam **3–7 hari kerja**. Begitu disetujui, status berubah menjadi **Verified** dan tidak ada lagi batasan 100 user!

---

## 🛠️ Bagian 3: Panduan Self-Host (Bagi Mahasiswa yang Mau Bikin Project Sendiri)

Jika ada teman yang ingin 100% mandiri menggunakan Google Cloud Project milik mereka sendiri:

1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat Project Baru: Klik **Select a Project** -> **New Project** (Beri nama: *Asisten-Akademik-Saya*).
3. Aktifkan API:
   * Masuk ke menu **APIs & Services** -> **Library**.
   * Cari dan klik **Enable** untuk:
     - **Google Calendar API**
     - **Google Tasks API**
4. Konfigurasi OAuth Consent Screen:
   * Masuk ke **APIs & Services** -> **OAuth consent screen**.
   * Pilih **User Type: External** -> Klik **Create**.
   * Masukkan App Name (*Asisten Saya*), User Support Email, dan Developer Email.
   * Pada tab **Scopes**, tambahkan scope Calendar dan Tasks.
   * Pada tab **Test users**, tambahkan alamat email Google pribadi mereka.
5. Buat Kredensial OAuth:
   * Masuk ke **APIs & Services** -> **Credentials**.
   * Klik **Create Credentials** -> **OAuth client ID**.
   * Application type: **Desktop app**.
   * Klik **Create**, lalu klik tombol **Download JSON** (simpan file sebagai `~/.hermes/google_client_secret.json`).
6. Jalankan autentikasi di terminal:
   ```bash
   python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --client-secret ~/.hermes/google_client_secret.json
   python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url
   ```
