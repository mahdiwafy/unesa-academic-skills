# 📖 Panduan Mandiri Integrasi Mendeley API & OAuth 2.0

Panduan ini menjelaskan cara menghubungkan akun **Mendeley Reference Manager** pribadi Anda ke asisten AI secara **100% mandiri, aman, dan gratis** menggunakan Mendeley Developer Portal resmi dari Elsevier.

> **Prinsip Privasi & Keamanan:** Seluruh token autentikasi, kredensial client, dan metadata pustaka disimpan secara lokal di mesin Anda (`~/.hermes/credentials/`). Tidak ada data riset atau kredensial yang dibagikan ke pihak ketiga.

---

## ⚡ Mengapa Mengintegrasikan Mendeley ke Asisten AI?

1. 🚀 **Input Referensi Otomatis:** Cukup berikan judul atau DOI, asisten AI langsung mengunduh metadata dan mendaftarkannya ke akun Mendeley Anda.
2. 📄 **Sinkronisasi File PDF Jurnal:** Asisten AI dapat mengunggah berkas PDF naskah langsung ke cloud Mendeley sehingga langsung tersedia di Mendeley Desktop & Web.
3. 🎯 **Bebas Kesalahan Sitasi:** Tidak ada lagi salah ketik nama penulis atau tahun terbit saat menyusun naskah tugas/skripsi berformat APA 7th Edition.

---

## 🛠️ Langkah Setup Mendeley OAuth Mandiri (~3 Menit)

### Langkah 1: Buka Mendeley Developer Portal
1. Kunjungi portal resmi developer Mendeley di: [https://dev.mendeley.com/](https://dev.mendeley.com/)
2. Klik tombol **"My Applications"** di menu bagian atas.
3. Login menggunakan akun Mendeley / Elsevier Anda (bisa akun personal atau akun kampus yang terdaftar di Mendeley).

---

### Langkah 2: Buat Aplikasi Baru (Register Application)
1. Setelah masuk ke halaman *My Applications*, klik tombol **"Create a new application"**.
2. Isi formulir pendaftaran aplikasi:
   * **Application name:** `Asisten Akademik Pribadi` (atau nama lain pilihan Anda).
   * **Redirect URL:** `http://localhost:8080` (wajib diisi ini agar alur OAuth berjalan mulus).
   * **Application description:** `Integrasi pustaka referensi untuk asisten AI akademik.`
3. Klik tombol **"Generate secret"** / **"Save"**.
4. Mendeley akan menampilkan dua nilai penting:
   * **App ID / Client ID** (berupa angka ID unik, misal: `12345`).
   * **Secret / Client Secret** (berupa string acak, misal: `kLx9...`).
   *(Simpan Secret ini karena hanya ditampilkan sekali saat dibuat).*

---

### Langkah 3: Simpan Kredensial di Direktori Lokal
Buat direktori kredensial dan simpan konfigurasi client dalam berkas JSON:

```bash
mkdir -p ~/.hermes/credentials
cat > ~/.hermes/credentials/mendeley.json << 'EOF'
{
  "client_id": "MASUKKAN_CLIENT_ID_ANDA",
  "client_secret": "MASUKKAN_CLIENT_SECRET_ANDA",
  "redirect_uri": "http://localhost:8080"
}
EOF
chmod 600 ~/.hermes/credentials/mendeley.json
```

---

### Langkah 4: Otorisasi Login Pertama Kali
1. Buka terminal dan jalankan perintah untuk mendapatkan URL otorisasi login:
   ```bash
   python3 ~/.hermes/skills/academic/academic-reference-manager/scripts/mendeley_service.py auth-url
   ```
2. Salin URL yang muncul, lalu buka di browser laptop Anda.
3. Login ke akun Mendeley Anda dan klik **"Accept / Authorize"**.
4. Browser akan mencoba mengarah ke `http://localhost:8080/?code=KODE_OTORISASI_ANDA`.
5. Salin teks kode yang ada di belakang `code=` pada address bar browser Anda.
6. Masukkan kode tersebut ke terminal:
   ```bash
   python3 ~/.hermes/skills/academic/academic-reference-manager/scripts/mendeley_service.py auth-code "KODE_OTORISASI_ANDA"
   ```
7. **Selesai!** File token akan tersimpan secara otomatis di `~/.hermes/credentials/mendeley_tokens.json`.

---

## 💡 Cara Kerja Token Refresh Otomatis

Access token Mendeley memiliki masa aktif terbatas. Script `mendeley_service.py` telah dilengkapi mekanisme **Auto Token Refresh**:
* Jika token kadaluarsa (HTTP 401), sistem secara otomatis memakai `refresh_token` untuk meminta token baru ke server Mendeley.
* Anda **tidak perlu mengulang proses login di browser** selama `refresh_token` tetap valid.

---

## 📚 Contoh Perintah Penggunaan Harian

| Perintah | Deskripsi |
| :--- | :--- |
| `python3 mendeley_service.py list` | Menampilkan seluruh dokumen di perpustakaan Mendeley Anda. |
| `python3 mendeley_service.py search "keyword"` | Mencari paper berdasarkan kata kunci judul/abstrak/penulis. |
| `python3 mendeley_service.py add --title "..." --doi "..."` | Menambahkan referensi artikel baru. |
| `python3 mendeley_service.py upload-file "<DOC_ID>" "path/to/paper.pdf"` | Mengunggah berkas PDF naskah ke dokumen Mendeley. |
| `python3 mendeley_service.py delete "<DOC_ID>"` | Menghapus dokumen yang tidak dibutuhkan lagi. |

---

## 🤝 Sinergi dengan Skill Lainnya

* **Dengan `smart-study-and-research`:** Setiap kali selesai membedah jurnal (analisis latar belakang, metodologi, temuan), asisten AI dapat langsung mendaftarkan jurnal tersebut ke Mendeley lengkap dengan PDF-nya.
* **Dengan `unesa-academic-standards`:** Asisten AI memeriksa kesesuaian kutipan di dalam teks makalah dengan daftar pustaka di Mendeley, serta mengekspor format sitasi BibTeX (`.bib`) dan RIS (`.ris`).
