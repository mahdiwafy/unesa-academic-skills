---
name: academic-life-schedule
description: "Kelola jadwal akademik dan kehidupan mahasiswa secara aman: ekstrak agenda, upsert Google Calendar, Google Tasks deadline, reminder, buffer perjalanan, dan anti-duplikasi."
tags: [unesa, academic, schedule, life, google-calendar, google-tasks, deadline, reminder, planning]
---

# Academic & Life Schedule Intelligence

Skill untuk mengubah informasi akademik dan agenda hidup menjadi sistem jadwal yang rapi, tidak duplikat, dan mudah ditindaklanjuti. Cocok untuk mahasiswa yang menerima informasi dari chat kelas, dosen, screenshot, LMS, Google Forms, atau rencana pribadi.

> **Prinsip utama:** kalender adalah sumber kebenaran untuk acara yang memiliki waktu; Google Tasks adalah tempat deadline, persiapan, dan checklist. Jangan mencampur keduanya.

---

## 1. Klasifikasi: Calendar vs Tasks vs Tidak Diubah

### A. Google Calendar — acara yang time-bounded
Masukkan ke kalender hanya bila ada waktu yang cukup jelas dan pengguna memang terlibat:

* Kuliah rutin, kelas pengganti, praktikum, ujian, TEP, bimbingan.
* Meeting organisasi, rapat kelompok, konsultasi dosen, janji temu.
* Acara pribadi yang dikonfirmasi: dokter, perjalanan, keluarga, kegiatan komunitas.

Setiap event minimal berisi:
* Judul yang spesifik.
* Waktu mulai dan selesai dengan zona waktu **Asia/Jakarta (WIB, UTC+07:00)**.
* Lokasi atau tautan meeting, jika tersedia.
* Sumber informasi dan catatan perubahan.

### B. Google Tasks — tenggat dan tindakan
Gunakan Tasks untuk:
* Deadline tugas, upload LMS, presensi, formulir wajib.
* Persiapan ujian/presentasi, membaca materi, mencetak berkas, membawa perlengkapan.
* Follow-up pribadi yang tidak memiliki slot waktu khusus.

Buat **subtask/checklist** untuk pekerjaan kompleks, misalnya: riset -> outline -> draf -> revisi -> ekspor PDF -> upload -> verifikasi terkirim.

### C. Jangan otomatis dibuat
Jangan membuat event maupun task dari:
* Pamflet umum, webinar/lomba/ormawa yang belum dinyatakan akan diikuti pengguna.
* Informasi tanpa tanggal/jam yang belum jelas.
* Pesan ambigu, rumor grup, atau jadwal yang belum disetujui dosen.

Buat proposal ringkas atau minta klarifikasi hanya jika keputusan pengguna benar-benar diperlukan.

---

## 2. Protokol Kepercayaan Informasi

Urutkan tingkat kepercayaan sumber:

1. **Konfirmasi eksplisit pengguna / dosen / surat edaran resmi** -> boleh dibuat atau diperbarui.
2. **Pengumuman grup kelas oleh PJ/Komti dengan tanggal, jam, dan konteks jelas** -> buat sebagai *proposed* atau *confirmed* sesuai mode pengguna.
3. **Informasi parsial** -> simpan sebagai catatan/tugas follow-up, bukan event final.

Mode standar untuk pengguna baru adalah **review-first**: rangkum perubahan lalu minta persetujuan sebelum menulis kalender. Mode **auto-sync** hanya dipakai bila pengguna secara eksplisit mengaktifkannya untuk sumber yang dipercaya (misalnya jadwal kuliah resmi atau kalender akademik yang sudah terhubung).

---

## 3. Algoritma Anti-Duplikasi & Perubahan Jadwal

Sebelum membuat apa pun:

1. Cari event kalender pada rentang waktu yang relevan dan Tasks aktif maupun selesai.
2. Cocokkan secara semantik: mata kuliah/topik + tanggal + peserta/lokasi + tautan pertemuan.
3. Bila event sama ditemukan, **patch event yang ada**, jangan membuat event kedua.
4. Bila jam, mode, lokasi, link, atau status berubah, perbarui event yang sama dan tambahkan catatan perubahan.
5. Bila kegiatan dibatalkan, tandai/dihapus sesuai preferensi pengguna. Jangan biarkan event lama menyesatkan.
6. Bila formulir atau tugas sudah berstatus selesai, jangan membuat ulang hanya karena link dibagikan kembali.

Gunakan ID event/task sebagai identitas stabil setelah dibuat. Jangan bergantung pada judul saja.

---

## 4. Template Event Akademik

### Kuliah Reguler
```text
[MK] Sistem Operasi — Pertemuan 04
Waktu: 2026-10-12 09:40–12:10 WIB
Lokasi: Gedung/Lab … atau [DARING] <link>
Deskripsi:
- Topik: Penjadwalan CPU
- Sumber: Pengumuman dosen/PJ MK tanggal …
- Persiapan: Baca modul 4, bawa laptop bila praktikum.
```

### Deadline Tugas (Google Tasks)
```text
[TUGAS] Sistem Operasi — Laporan Praktikum 2
Jatuh tempo: 2026-10-14 23:59 WIB
Checklist:
- Analisis hasil uji
- Validasi format DOCX/PDF
- Upload ke LMS
- Cek status "Submitted"
Sumber: …
```

### Kelas Pengganti / Perubahan
```text
🔄 [PENGGANTI] Algoritma Pemrograman
Waktu baru: …
Menggantikan: Pertemuan …
Mode: Daring/Luring
Link/Ruang: …
Perubahan diumumkan oleh: …
```

---

## 5. Smart Buffers & Reminder

Saat menyusun jadwal, pertimbangkan konteks nyata:

* Tambahkan pengingat 1 hari dan 60–90 menit sebelum ujian/presentasi/pemberangkatan penting.
* Tambahkan buffer perjalanan untuk perpindahan kampus/lokasi, terutama jika jarak atau jam rawan macet.
* Hindari penempatan tugas berat pada jam kuliah atau agenda yang sudah padat.
* Untuk deadline malam, buat task persiapan lebih awal (contoh H-3 riset, H-1 revisi), bukan hanya task pada menit terakhir.

Jangan mengirim notifikasi berulang untuk agenda yang sama tanpa adanya perubahan material.

---

## 6. Integrasi Google (OAuth yang Aman untuk Setiap Pengguna)

Gunakan OAuth **milik masing-masing pengguna**. Jangan pernah menyalin token, file `google_token*.json`, atau OAuth client secret dari pengguna lain.

### Scope minimum untuk scheduler
Mulai dari scope yang paling sempit:

* Google Calendar: `https://www.googleapis.com/auth/calendar.events.owned` bila aplikasi hanya mengelola event di kalender milik pengguna.
* Google Tasks: `https://www.googleapis.com/auth/tasks` bila aplikasi perlu membuat/menandai task.

Jangan meminta Gmail, Drive, Contacts, atau akses kalender penuh jika fitur tersebut tidak diperlukan.

### Integrasi dengan Hermes Agent
1. Hubungkan akun Google pengguna melalui OAuth consent flow mereka sendiri.
2. Pastikan status autentikasi berhasil.
3. Baca agenda sebelum create event/task.
4. Gunakan update/upsert ketika event atau task terkait sudah ada.
5. Simpan token terenkripsi di mesin akun pengguna; token tidak boleh masuk Git, chat, log publik, atau repository.

Lihat `docs/GOOGLE_OAUTH_DEPLOYMENT.md` di repository utama untuk model distribusi, scope, dan perbedaan pilot vs produk komersial.

---

## 7. Privacy by Default

* Event pribadi diberi visibility `private` jika API/platform mendukungnya.
* Jangan menyalin isi percakapan pribadi ke deskripsi kalender. Simpan ringkasan minimal yang diperlukan.
* Jangan menyebarkan kalender, daftar tugas, atau identitas akademik pengguna ke grup tanpa persetujuan eksplisit.
* Sediakan kemampuan menghapus koneksi akun dan token bila pengguna berhenti memakai layanan.
