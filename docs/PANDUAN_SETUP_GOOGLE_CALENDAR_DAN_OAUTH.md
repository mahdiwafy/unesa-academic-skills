# 📖 Panduan Mandiri Integrasi Google Calendar & Tasks

Panduan ini menjelaskan cara menghubungkan akun Google pribadi / kampus ke asisten AI secara **100% mandiri, aman, dan gratis** menggunakan Google Cloud Console masing-masing pengguna.

> **Prinsip Privasi:** Tidak ada token, password, atau jadwal pribadi yang dibagikan ke server pihak ketiga. Seluruh konfigurasi dan token autentikasi disimpan secara lokal dan privat di perangkat Anda sendiri.

---

## ⚡ Langkah Mudah: Setup Google OAuth Mandiri (Sekali Setup, ~3 Menit)

### Langkah 1: Buat Project Gratis di Google Cloud
1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Login menggunakan akun Google Anda (bisa akun personal `@gmail.com` atau akun kampus).
3. Klik dropdown project di bagian atas (sebelah logo Google Cloud) -> Klik **"New Project"**.
4. Beri nama project, misalnya: `Asisten-Akademik-Pribadi` -> Klik **Create**.

---

### Langkah 2: Aktifkan API Calendar & Tasks
1. Di sidebar kiri, buka menu **APIs & Services** -> **Library**.
2. Cari **"Google Calendar API"** -> Klik dan tekan tombol **Enable**.
3. Kembali ke Library, cari **"Google Tasks API"** -> Klik dan tekan tombol **Enable**.

---

### Langkah 3: Konfigurasi Layar Persetujuan (OAuth Consent Screen)
1. Di menu sebelah kiri, klik **APIs & Services** -> **OAuth consent screen**.
2. Pilih User Type: **External** -> Klik **Create**.
3. Isi data dasar aplikasi:
   * **App name:** `Asisten Akademik` (atau nama pilihan Anda).
   * **User support email:** Pilih email Google Anda.
   * **Developer contact information:** Masukkan email Google Anda.
   * Klik **Save and Continue**.
4. Pada tab **Scopes**, klik **Add or Remove Scopes**:
   * Centang `/auth/calendar.events` (atau `/auth/calendar`) untuk izin kalender.
   * Centang `/auth/tasks` untuk izin tugas/deadline.
   * Klik **Update** -> Klik **Save and Continue**.
5. Pada tab **Test users**:
   * Klik **+ Add Users**, lalu masukkan alamat email Google Anda sendiri.
   * Klik **Save and Continue**.

---

### Langkah 4: Buat Kredensial OAuth (Desktop Client)
1. Di menu sebelah kiri, klik **APIs & Services** -> **Credentials**.
2. Klik tombol **+ Create Credentials** di bagian atas -> Pilih **OAuth client ID**.
3. Pilih Application type: **Desktop app**.
4. Beri nama (misal `Asisten Desktop Client`) -> Klik **Create**.
5. Jendela konfirmasi akan muncul. Klik tombol **Download JSON** (ikon unduh panah ke bawah).

---

### Langkah 5: Pasang Kredensial & Autentikasi
1. Pindahkan atau simpan file JSON yang baru diunduh ke direktori asisten Anda, misalnya:
   ```bash
   cp ~/Downloads/client_secret_*.json ~/.hermes/google_client_secret.json
   ```
2. Jalankan perintah inisialisasi login di terminal:
   ```bash
   python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --client-secret ~/.hermes/google_client_secret.json
   python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url
   ```
3. Buka URL login yang muncul di browser, klik akun Google Anda, berikan centang izin akses Calendar & Tasks, lalu salin URL hasil redirect `http://localhost:1/?code=...` kembali ke terminal:
   ```bash
   python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "URL_YANG_DISALIN"
   ```
4. **Selesai!** Akun Google Calendar & Tasks Anda sudah terhubung secara privat di mesin Anda sendiri.
