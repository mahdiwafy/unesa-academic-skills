# 🎓 UNESA Academic Skill Pack (Mahasiswa AI Supercharger)

[![Hermes Agent](https://img.shields.io/badge/Hermes_Agent-Ready-blue.svg)](https://hermes-agent.nousresearch.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![UNESA](https://img.shields.io/badge/Kampus-UNESA-yellow.svg)](https://unesa.ac.id)
[![Anti-AI Slop](https://img.shields.io/badge/Standard-Anti--AI--Slop-red.svg)](#)

Kumpulan **Skill & Standar Operasional Prosedur (SOP) Akademik** untuk AI Agent ([Hermes Agent](https://hermes-agent.nousresearch.com), Claude Code, Cursor, Windsurf) maupun Web AI (ChatGPT, Claude, Gemini). Dirancang khusus untuk mahasiswa Universitas Negeri Surabaya (UNESA) dan perguruan tinggi di Indonesia agar hasil pengerjaan tugas, makalah, presentasi, dan komunikasi kampus memiliki kualitas tinggi, presisi, dan bebas dari halusinasi/bahasa klise AI (*anti-slop*).

---

## 🌟 Mengapa Skill Pack Ini Dibuat?

Sering kali hasil generasi AI generik memiliki masalah umum:
1. ❌ **Format Makalah Hancur:** Margin default US Letter, penomoran bab gaya luar negeri, dan spasi berantakan.
2. ❌ **Bahasa Klise (*AI Slop*):** Paragraf selalu diawali *"Dalam era globalisasi yang serba cepat ini..."* atau *"Tak dapat dipungkiri bahwa..."*.
3. ❌ **Chat Dosen Kaku / Kurang Sopan:** Format pesan kurang mencerminkan etika akademik Indonesia (kurang identitas diri atau waktu yang tepat).
4. ❌ **Slide Presentasi Terlalu Penuh:** AI menumpuk teks 1 bab ke dalam 1 slide tanpa *speaker notes*.
5. ❌ **Laporan Praktikum Tanpa Analisis:** Hanya menempelkan kode tanpa analisis alur logika per-blok.

**UNESA Academic Skill Pack menyelesaikan semua masalah di atas secara otomatis.**

---

## 📦 Daftar Skill yang Termasuk

| Nama Skill | Deskripsi & Kegunaan |
| :--- | :--- |
| **`unesa-academic-standards`** | Standar penulisan karya ilmiah, makalah, dan skripsi format A4, margin baku (4-4-3-3 / 3-3-3-3), Times New Roman 12 pt spasi 1.5, sitasi APA 7th / IEEE, serta generator file `.docx` otomatis. |
| **`unesa-communication-hub`** | Panduan etika chat dosen (DPA, Dosen Pengampu, Koorprodi), template broadcast Komti/PJ MK ke grup kelas, serta surat izin tidak masuk kuliah/dispensasi. |
| **`academic-presentation-mastery`** | Arsitektur pembuatan slide kuliah 8–12 slide efektif (Aturan 6x6, anti wall-of-text) dilengkapi naskah contekan bicara (*Speaker Notes*) berdurasi 60–90 detik per slide. |
| **`lab-and-coding-practical`** | Standar pengerjaan laporan praktikum laboratorium (Informatika, Elektro, Sains, MIPA) dengan analisis logika kode per-blok dan standar kebersihan Jupyter Notebook (`.ipynb`). |
| **`smart-study-and-research`** | Framework bedah jurnal ilmiah cepat (SINTA & Scopus), penyusunan sintesis literatur, flashcards konsep, serta bank soal latihan (C3–C5 Problem Solving) untuk persiapan UTS/UAS. |
| **`unesa-portal-guide`** | Panduan navigasi alur sistem digital kampus UNESA: Siakadu (KRS/KHS), SSO UNESA, Vinesa (LMS Moodle), SiDia (Presensi), dan TEP Pusat Bahasa LPSP. |

---

## 🚀 Cara Pemasangan (Instalasi)

### 1. Pengguna Hermes Agent (Direkomendasikan ⚡)

Jika kamu menggunakan **Hermes Agent**, jalankan perintah satu baris berikut di terminal:

```bash
# Clone dan pasang langsung ke folder ~/.hermes/skills/
git clone https://github.com/mahdiwafy/unesa-academic-skills.git /tmp/unesa-pack && \
bash /tmp/unesa-pack/install.sh && \
rm -rf /tmp/unesa-pack
```

Atau salin folder repository ini ke `~/.hermes/skills/academic/`.

---

### 2. Pengguna Claude Code / Cursor / Windsurf

Salin folder `skills/` ke dalam direktori project atau workspace kamu, atau tambahkan aturan di `.cursorrules` / `.cursor/rules/`:

```bash
# Tambahkan skill ke rules proyek
mkdir -p .cursor/rules
cp -r skills/* .cursor/rules/
```

---

### 3. Pengguna ChatGPT / Claude Web / Gemini

Jika kamu menggunakan web chat biasa (ChatGPT Plus/Free, Claude.ai, Gemini):
1. Buka file **[`UNESA_ACADEMIC_PROMPT_BUNDLE.md`](UNESA_ACADEMIC_PROMPT_BUNDLE.md)** di repo ini.
2. Copy seluruh isinya.
3. Paste ke dalam **Custom Instructions** (ChatGPT) atau **Project Instructions** (Claude Projects).

---

## 💡 Contoh Penggunaan (Prompting)

Setelah skill terpasang, kamu cukup memberi instruksi sederhana ke AI kamu:

### 1. Membuat Makalah Kuliah
> *"Buatkan draf BAB I Pendahuluan untuk makalah mata kuliah Sistem Operasi dengan topik 'Analisis Efisiensi Algoritma Penjadwalan CPU'. Terapkan standar unesa-academic-standards lengkap dengan margin dan format heading baku."*

### 2. Menghubungi Dosen Pengampu
> *"Bantu buatkan chat WhatsApp yang sopan ke Ibu Dosen Dr. Sri Wahyuni untuk menanyakan konfirmasi kelas pengganti hari Rabu jam 10.00 WIB di ruang R.302."*

### 3. Merancang Slide Presentasi & Speaker Notes
> *"Rancang materi presentasi 10 slide tentang 'Keamanan Database Terdistribusi' untuk tugas kelompok. Sertakan poin visual slide dan speaker notes naskah bicaranya."*

### 4. Menyusun Laporan Praktikum
> *"Bantu susun laporan praktikum modul 3 Struktur Data: Binary Search Tree dalam C++. Sertakan penjelasan logika kode per blok dan troubleshooting log-nya."*

### 5. Membedah Paper Jurnal
> *"Bedah artikel jurnal terlampir ini menggunakan format matrix telaah ilmiah 5 menit (Research gap, metodologi, temuan utama, dan limitasi)."*

---

## 🛠️ Script Pembantu Tambahan

Di dalam folder `skills/unesa-academic-standards/scripts/`, tersedia script python untuk menghasilkan dokumen Word yang langsung tersetting A4 dan margin rapi:

```bash
python3 skills/unesa-academic-standards/scripts/generate_docx.py \
  --title "Penerapan Machine Learning pada Prediksi Cuaca" \
  --author "Ahmad Fauzi" \
  --nim "26050974001" \
  --prodi "Pendidikan Teknologi Informasi" \
  --out "Makalah_Final.docx"
```

---

## 📄 Lisensi & Kontribusi

Repository ini dirilis di bawah lisensi **MIT**. Silakan digunakan, dimodifikasi, dan dibagikan secara bebas kepada seluruh civitas akademika dan rekan-rekan mahasiswa.

Dibuat dengan ❤️ untuk kemajuan riset dan studi mahasiswa UNESA.
