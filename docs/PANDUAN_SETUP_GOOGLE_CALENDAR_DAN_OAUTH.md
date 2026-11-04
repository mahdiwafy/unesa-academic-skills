# 📖 Panduan Integrasi Google Workspace (Sheets, Docs, Drive, Photos, Calendar, Tasks)

Panduan menghubungkan akun Google Anda (Personal `@gmail.com` atau Kampus `@mhs.unesa.ac.id`) ke AI Agent untuk mengakses Google Sheets, Google Docs, Google Drive, Google Photos, Calendar, dan Tasks secara **100% lokal, aman, dan privat**.

> **Prinsip Privasi:** Tidak ada token, password, atau berkas pribadi yang dibagikan ke server pihak ketiga. Seluruh konfigurasi dan token autentikasi disimpan secara lokal dan privat di perangkat Anda (`~/.hermes/`).

---

## ⚡ OPSI 1: Setup Kilat 1-Klik (Direkomendasikan ⚡)

Anda **TIDAK PERLU** membuat project di Google Cloud Console atau mengunduh JSON manual. Repositori ini telah menyertakan kredensial resmi **Agent Connect**:

### 1. Dapatkan Link Login Google
Jalankan di terminal:
```bash
python3 skills/academic-google-workspace/scripts/setup_google.py --auth-url --account personal
```
*(Gunakan `--account sso` untuk menautkan akun kampus UNESA).*

### 2. Otorisasi Akun di Browser
1. Buka tautan URL yang muncul di browser Anda.
2. Layar persetujuan resmi Google akan menampilkan: **"Lanjutkan ke Agent Connect"**.
3. Pilih akun Google Anda, centang izin akses (Drive, Docs, Sheets, Photos, Calendar, Tasks), lalu klik **Lanjutkan / Izinkan**.
4. Salin URL hasil pengalihan (redirect) dari address bar browser (`http://localhost/?code=4/0A...`).

### 3. Masukkan Kode Otorisasi
Tempelkan URL atau kode yang telah disalin ke terminal:
```bash
python3 skills/academic-google-workspace/scripts/setup_google.py --auth-code "KODE_ATAU_URL_HASIL_REDIRECT" --account personal
```

**Selesai!** Akun Google Anda telah resmi terhubung ke AI Agent.

---

## 🛠️ OPSI 2: Setup Mandiri di Google Cloud Console (Opsional)

Jika Anda ingin menggunakan Google Cloud Project milik Anda sendiri:

1. Buka [Google Cloud Console](https://console.cloud.google.com/) dan buat project baru.
2. Aktifkan API yang dibutuhkan di menu **APIs & Services -> Library**:
   * Google Drive API
   * Google Sheets API
   * Google Docs API
   * Google Calendar API
   * Google Tasks API
   * Photos Library API
3. Di menu **OAuth consent screen**:
   * Set nama aplikasi: `Agent Connect`
   * Masukkan email dukungan dan developer.
   * Tambahkan Scopes yang dibutuhkan.
4. Di menu **Credentials**:
   * Klik **+ Create Credentials** -> **OAuth client ID** -> Tipe: **Desktop app**.
   * Unduh file JSON kredensial.
5. Simpan file kredensial Anda:
   ```bash
   python3 skills/academic-google-workspace/scripts/setup_google.py --client-secret ~/Downloads/client_secret_*.json
   ```
6. Jalankan autentikasi seperti pada Opsi 1.
