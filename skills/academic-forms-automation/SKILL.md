---
name: academic-forms-automation
description: "Otomasi Google Forms akademik: inspeksi struktur pertanyaan, pembuatan Cloud Draft tersimpan (Chrome CDP) untuk upload berkas & login SSO, serta generator draf instan URL (usp=pp_url)."
tags: [unesa, academic, google-forms, gform, cloud-draft, cdp, automation, presensi, sso]
---

# Academic Google Forms Automation & Cloud Draft Engine

Skill untuk menangani otomatisasi formulir Google Forms kampus (presensi perkuliahan, pengumpulan tugas makalah/laporan, pendataan ukuran jas lab/almamater, kuesioner evaluasi, dan pendaftaran kegiatan mahasiswa) menggunakan arsitektur **Dual-Engine**: **Cloud Draft Autosave** (via Chrome CDP) dan **Instant Prefilled URL** (`usp=pp_url`).

---

## 1. Arsitektur Dual-Engine: Pilih Sesuai Kebutuhan

| Aspek | Mode 1: Cloud Draft (via Chrome CDP :9222) | Mode 2: Prefilled URL (`usp=pp_url`) |
| :--- | :--- | :--- |
| **Kecepatan** | 5–15 detik | Sub-detik (~300 milidetik) |
| **Beban Komputasi** | Membuka tab Chrome aktif | Sangat ringan (HTTP GET murni) |
| **Upload Berkas** | ✅ **Bisa** (otomatis unggah via Google Picker) | ❌ **Tidak Bisa** (limitasi Google Forms) |
| **Login Google / SSO**| ✅ **Tersimpan ke Akun** (Cloud Draft terikat) | ⚠️ Terbuka di profil aktif pengguna saat klik |
| **Kenyamanan** | Draf langsung tersimpan di server Google, buka di HP langsung terisi | Dikirimkan link siap klik berisi isian jawaban |
| **Kapan Digunakan** | Formulir ada upload file, login-wall kampus, atau user minta simpan draf | Presensi kilat, survei teks/angka/pilihan ganda |

---

## 2. Struktur Pertanyaan & Ekstraksi Metadata (`FB_PUBLIC_LOAD_DATA_`)

Google Forms menyimpan seluruh struktur pertanyaan, tipe field, dan opsi pilihan ganda dalam variabel JavaScript `FB_PUBLIC_LOAD_DATA_` di dalam HTML halaman formulir.

### Tipe Pertanyaan Google Forms:
* **Tipe 0:** Jawaban Singkat (*Short Text*)
* **Tipe 1:** Paragraf (*Long Text*)
* **Tipe 2:** Pilihan Ganda (*Multiple Choice / Radio*)
* **Tipe 3:** Dropdown (*Listbox Option*)
* **Tipe 4:** Kotak Centang (*Checkboxes*)
* **Tipe 5:** Skala Linier (*Linear Scale*)
* **Tipe 7:** Kisi Pilihan Ganda (*Grid Matrix*)
* **Tipe 9:** Tanggal (*Date*)
* **Tipe 10:** Waktu (*Time*)
* **Tipe 13:** Unggah Berkas (*File Upload / Google Picker*)

### Perintah Inspeksi Cepat:
Gunakan script pembantu `gform_tool.py` untuk melihat seluruh pertanyaan dan entry ID tanpa membuka browser:

```bash
python3 skills/academic-forms-automation/scripts/gform_tool.py inspect "https://forms.gle/contohLink"
```

Output akan menampilkan judul form, nomor urut, ID masukan (`entry.XXXXX`), tipe input, status wajib/opsional, dan opsi pilihan.

---

## 3. Mode Utama: Cloud Draft Autosave (via Chrome CDP :9222)

Ketika formulir mewajibkan upload berkas (misal: bukti pembayaran, laporan praktikum PDF, foto KTM), atau ketika pengguna ingin draf sudah tersimpan aman di akun Google mereka:

### A. Alur Kerja Otomasi Cloud Draft:
1. **Navigasi Profil SSO:** Tambahkan parameter `authuser=<email_sso>` pada URL formulir agar Chrome membuka halaman dengan identitas akun kampus mahasiswa yang tepat (bukan akun personal).
2. **Penanganan Consent Checkbox Email:** Formulir kampus sering kali mewajibkan perekaman email respons. Periksa elemen `div[role="checkbox"]` untuk persetujuan perekaman email dan centang jika belum aktif (`aria-checked="false"`).
3. **Pengisian Field Input:**
   * Kolom teks (`input[type="text"]`, `input[type="email"]`, `textarea`) diisi menggunakan simulasi pengetikan alami untuk mengaktifkan *dirty-state listener* Google.
   * Dropdown (`div[role="listbox"]`) diklik untuk membuka menu opsi, lalu opsi yang sesuai dipilih.
   * Radio button (`div[role="radio"]`) dicocokkan berdasarkan atribut `data-value` atau teks label.
4. **Otomasi Upload Berkas (Google Picker):**
   * **Draft Restore Trap Guard:** Sebelum mengklik tombol *"Tambahkan file"*, cek terlebih dahulu apakah nama berkas sudah muncul di DOM naskah (karena jika draf sebelumnya telah menyimpan file tersebut, tombol *Add file* disembunyikan oleh CSS `display: none` dan akan memicu error timeout jika dipaksa klik).
   * Jika belum terunggah, klik tombol *"Tambahkan file"*, cari iframe modal Google Picker, dan injeksikan berkas ke elemen `<input type="file">` yang tersembunyi (`state="attached"`).
   * Tekan tombol `Escape` untuk menutup backdrop modal setelah upload selesai.
5. **Verifikasi Indikator Cloud Draft:**
   * Tunggu hingga indikator di bagian atas formulir berganti dari *"Menyimpan..."* menjadi *"Draf disimpan"* (*"Draft saved"*).
   * Ambil tangkapan layar (screenshot) sebagai bukti verifikasi draf berhasil tersimpan.

### B. Menjalankan Cloud Draft via CLI:
```bash
python3 skills/academic-forms-automation/scripts/gform_tool.py cloud-draft \
  "https://docs.google.com/forms/d/e/.../viewform" \
  --authuser "mahasiswa@mhs.unesa.ac.id" \
  --profile "scripts/profile.json.example" \
  --file "laporan=~/tugas/Laporan_Praktikum.pdf" \
  --screenshot "/tmp/draft_bukti.png"
```

---

## 4. Mode Cepat: Instant Prefilled Draf URL (`usp=pp_url`)

Untuk formulir presensi kilat atau pendataan teks tanpa berkas, pembuatan link prefilled adalah opsi paling instan (~300ms) tanpa memakan memori browser.

### A. Alur Pembuatan URL Prefill:
1. Hubungkan `entry.XXXXX` dengan profil mahasiswa (Nama, NIM, Program Studi, Kelas).
2. Susun parameter URL query:
   ```text
   https://docs.google.com/forms/d/e/<FORM_ID>/viewform?authuser=mahasiswa@mhs.unesa.ac.id&usp=pp_url&entry.1000001=Nama+Mahasiswa&entry.1000002=26050974001&entry.1000003=Hadir
   ```
3. Serahkan link tersebut ke mahasiswa di chat. Saat link dibuka di browser smartphone/laptop, seluruh formulir sudah terisi lengkap. Mahasiswa cukup klik **Kirim / Submit**.

### B. Menjalankan Generator Prefill via CLI:
```bash
python3 skills/academic-forms-automation/scripts/gform_tool.py prefill \
  "https://forms.gle/contohLink" \
  --authuser "mahasiswa@mhs.unesa.ac.id" \
  --data '{"entry.1000001": "Nama Mahasiswa", "entry.1000002": "26050974001", "entry.1000003": "Hadir"}'
```

---

## 5. Headless Submit & Ekstraksi Link Grup WhatsApp Onboarding

Jika formulir adalah absensi harian yang sudah dikonfirmasi valid dan tidak memerlukan review manual:

```bash
python3 skills/academic-forms-automation/scripts/gform_tool.py submit \
  "https://docs.google.com/forms/d/e/.../viewform" \
  --data '{"entry.1000001": "Nama Mahasiswa", "entry.1000002": "26050974001"}'
```

Script akan:
1. Menembakkan payload secara langsung ke endpoint `/formResponse`.
2. Memverifikasi teks konfirmasi respons (*"Jawaban Anda telah direkam"* / *"Your response has been recorded"*).
3. Mendeteksi dan mengekstrak tautan grup WhatsApp onboarding (`https://chat.whatsapp.com/...`) jika panitia menyematkannya pada halaman terima kasih.

---

## 6. Template Konfigurasi Profil Mahasiswa (`profile.json`)

Agar tidak menulis ulang identitas di setiap formulir, simpan konfigurasi profil di berkas lokal (contoh: `profile.json`):

```json
{
  "authuser": "mahasiswa@mhs.unesa.ac.id",
  "student": {
    "name": "Nama Mahasiswa",
    "nim": "26050974001",
    "prodi": "Pendidikan Teknologi Informasi",
    "angkatan": "2026",
    "kelas": "2026C",
    "ukuran_baju": "L"
  },
  "answers": {
    "entry.1000001": "Nama Mahasiswa",
    "entry.1000002": "26050974001",
    "entry.1000003": "Pendidikan Teknologi Informasi"
  }
}
```

> **Catatan Keamanan & Privasi:**
> Simpan `profile.json` di mesin lokal Anda (`~/.hermes/credentials/academic_profile.json`). Jangan pernah memasukkan identitas privat atau token ke dalam repositori publik.
