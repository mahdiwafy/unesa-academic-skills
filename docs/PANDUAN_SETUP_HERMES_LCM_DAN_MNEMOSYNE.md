# 🧠 Panduan Setup Hermes LCM (Long Context Memory) & Mnemosyne (Long-Term Memory)

Panduan lengkap instalasi, konfigurasi, dan pengoperasian dua sistem memori utama pada **Hermes Agent** untuk mewujudkan *Academic Second Brain* yang tidak pernah lupa:
1. **Hermes LCM (Long Context Memory):** Engine kompresi konteks otomatis berbasis Graph/DAG summarization. Mencegah token *out-of-memory* pada diskusi panjang (revisi makalah bab per bab, coding proyek berjam-jam) sambil mempertahankan detail penting melalui *semantic recall*.
2. **Mnemosyne:** Engine memori persisten lintas sesi (Three-Tier Memory Architecture) yang menyimpan fakta profil mahasiswa, dosen pengampu, progres skripsi/tugas, dan preferensi belajar secara permanen dalam database lokal SQLite + Vector embeddings.

---

## 🏗️ Arsitektur Memori AI Agent

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        HERMES ACADEMIC AGENT                           │
│                                                                        │
│   ┌───────────────────────────┐      ┌─────────────────────────────┐   │
│   │   HERMES LCM (Session)    │      │    MNEMOSYNE (Cross-Session)│   │
│   │                           │      │                             │   │
│   │ • Kompresi konteks obrolan│      │ • Profil Mahasiswa (Tier 1) │   │
│   │ • Ringkasan hierarki (DAG)│      │ • Progres Tugas/Matkul(T2)  │   │
│   │ • Hemat 60–80% token LLM  │      │ • Kebiasaan & Aturan (T3)   │   │
│   │ • Tools: lcm_grep, recall │      │ • Tools: mnemosyne_remember │   │
│   └─────────────┬─────────────┘      └──────────────┬──────────────┘   │
│                 │                                   │                  │
│                 ▼                                   ▼                  │
│   [SQLite: ~/.hermes/lcm.db]          [SQLite: ~/.hermes/mnemosyne.db] │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prasyarat Sistem

Sebelum memulai, pastikan mesin / server memenuhi kebutuhan berikut:
* **Hermes Agent:** Sudah terpasang dan dapat dijalankan (`hermes --version`).
* **Python:** Versi 3.10 atau lebih baru (`python3 --version`).
* **Lingkungan Linux/macOS:** Mendukung `systemd --user` (opsional jika berjalan sebagai daemon service).
* **API Key Embedding:** Memiliki endpoint embedding OpenAI-compatible (misal OpenAI `text-embedding-3-small`, atau proxy lokal/cloud) untuk pencarian vektor semantik.

---

## 1️⃣ LANGKAH 1: Setup Hermes LCM (Long Context Memory)

Hermes LCM bekerja di latar belakang setiap sesi percakapan. Ketika panjang konteks obrolan melebihi ambang batas (default: 70% batas konteks model), LCM secara otomatis meringkas pesan lama menjadi *summary nodes* tanpa memotong rantai penalaran.

### 1.1 Unduh Plugin Hermes LCM
Clone plugin resmi Hermes LCM ke direktori plugin Hermes:

```bash
git clone https://github.com/NousResearch/hermes-lcm.git ~/.hermes/plugins/hermes-lcm
cd ~/.hermes/plugins/hermes-lcm
pip install -r requirements.txt
cd ~
```

### 1.2 Konfigurasi Environment Variable
Konfigurasikan parameter LCM pada file environment atau systemd drop-in service (`~/.config/systemd/user/hermes-gateway.service.d/lcm.conf`):

```ini
[Service]
# Tuning Batas Kompresi LCM
Environment="LCM_SUMMARY_CIRCUIT_BREAKER_FAILURE_THRESHOLD=5"
Environment="LCM_CONTEXT_THRESHOLD=0.7"
Environment="LCM_FRESH_TAIL_COUNT=8"
Environment="LCM_LEAF_CHUNK_TOKENS=2000"
Environment="LCM_DYNAMIC_LEAF_CHUNK_ENABLED=true"
Environment="LCM_DYNAMIC_LEAF_CHUNK_MAX=20000"
Environment="LCM_CACHE_FRIENDLY_CONDENSATION_ENABLED=true"
Environment="LCM_DEFERRED_MAINTENANCE_ENABLED=true"
Environment="LCM_CONDENSATION_FANIN=3"
Environment="LCM_INCREMENTAL_MAX_DEPTH=3"

# Konfigurasi Semantic Embeddings (Pencarian Arti Kata)
Environment="LCM_EMBEDDINGS_ENABLED=true"
Environment="LCM_EMBEDDING_PROVIDER=openai_compatible"
Environment="LCM_EMBEDDING_MODEL=text-embedding-3-small"
Environment="LCM_OPENAI_COMPATIBLE_BASE_URL=https://api.openai.com/v1"
Environment="LCM_OPENAI_COMPATIBLE_API_KEY=sk-MASUKKAN_API_KEY_ANDA"
Environment="LCM_EMBEDDING_STORE_DIM=1536"
Environment="LCM_EMBEDDING_STORAGE_DTYPE=int8"
Environment="LCM_EMBEDDING_BINARY_PRESCREEN=true"
```

> **Tips Provider Bebas/Proxy:**
> Anda dapat mengganti `LCM_OPENAI_COMPATIBLE_BASE_URL` ke reverse proxy, local Ollama (`http://localhost:11434/v1`), atau penyedia AI lain. Sesuaikan `LCM_EMBEDDING_STORE_DIM` dengan dimensi model (contoh: 1536 untuk `text-embedding-3-small`, 768 untuk `nomic-embed-text`).

### 1.3 Aktifkan Kompresi di Hermes Config
Jalankan perintah konfigurasi CLI:

```bash
hermes config set compression.enabled true
```

### 1.4 Restart Gateway & Verifikasi
Jika menggunakan systemd:
```bash
systemctl --user daemon-reload
systemctl --user restart hermes-gateway
```

Periksa log apakah LCM telah aktif:
```bash
journalctl --user -u hermes-gateway -n 30 --no-pager | grep -i lcm
```

---

## 2️⃣ LANGKAH 2: Setup Mnemosyne (Permanent Long-Term Memory)

Mnemosyne adalah sistem memori permanen berbasis SQLite yang memungkinkan AI mengingat profil, mata kuliah, preferensi format dosen, dan riwayat tugas bahkan setelah sesi ditutup (`/new`) atau server direstart.

### 2.1 Pasang Paket Mnemosyne
Pasang library Mnemosyne ke dalam virtual environment Python yang digunakan oleh Hermes:

```bash
# Pastikan dipasang di Python virtual environment Hermes
~/.hermes/hermes-agent/venv/bin/python -m pip install --upgrade mnemosyne-memory mnemosyne-hermes

# Buat direktori plugins dan tautkan symlink jika diperlukan
mkdir -p ~/.hermes/plugins
```

### 2.2 Atur Memory Provider di Hermes
Ubah provider memori bawaan Hermes ke Mnemosyne:

```bash
hermes config set memory.provider mnemosyne
hermes config set memory.memory_enabled true
hermes config set memory.user_profile_enabled false
```

### 2.3 Buat Berkas Konfigurasi Mnemosyne (`~/.hermes/mnemosyne/config.yaml`)
Buat folder dan file konfigurasi:

```bash
mkdir -p ~/.hermes/mnemosyne
```

Tulis file `~/.hermes/mnemosyne/config.yaml`:
```yaml
# Konfigurasi Mesin Mnemosyne
enhanced_recall: true
polyphonic_recall: true
recall_diagnostics: false

# Bobot Scoring Hybrid Search (Total = 1.0)
vec_weight: 0.5          # 50% Kemiripan Vektor Semantik
fts_weight: 0.3          # 30% Full-Text Search (Kata Kunci Pasti)
importance_weight: 0.2   # 20% Tingkat Kepentingan Catatan

proactive_linking: true
persona_daily_sync_hour: 4
sleep_model_refresh_enabled: true
sleep_model_refresh_categories:
  - user
  - workflow
  - academic

# Pengaturan Model Embeddings
embedding_model: text-embedding-3-small
embedding_base_url: https://api.openai.com/v1
embedding_batch_size: 50
embedding_rate_limit_rpm: 500
api_key: sk-MASUKKAN_API_KEY_ANDA
```

### 2.4 Inisialisasi Database & Cek Kesehatan
Jalankan diagnosa CLI untuk memastikan database terbuat dan siap digunakan:

```bash
~/.hermes/hermes-agent/venv/bin/python -m mnemosyne.cli diagnose
```
Output yang sehat akan menampilkan status: `Database schema: OK`, `Vector index: OK`.

### 2.5 Restart Hermes Service
```bash
systemctl --user restart hermes-gateway
```

---

## 3️⃣ PENGGUNAAN & PENGUJIAN OLEH AI AGENT

Setelah kedua modul terpasang, agen Anda akan secara otomatis memiliki toolset memori tingkat lanjut:

### A. Mnemosyne Tools (Ingatan Permanen Lintas Sesi)

1. **Menyimpan Fakta / Profil (`mnemosyne_remember`):**
   ```python
   # Contoh menyimpan profil mahasiswa (Tier 1)
   mnemosyne_remember(
       content="Mahasiswa bernama Ahmad Fauzi, NIM 26050974001, S1 Pendidikan Teknologi Informasi UNESA angkatan 2026 kelas C.",
       category="user",
       importance=0.9
   )

   # Contoh menyimpan preferensi dosen (Tier 3)
   mnemosyne_remember(
       content="Dosen Pengampu Basis Data (Pak I Made) mewajibkan laporan praktikum menggunakan format font Arial 11 spasi 1.15.",
       category="academic",
       importance=0.8
   )
   ```

2. **Mengingat Kembali Informasi (`mnemosyne_recall`):**
   ```python
   # Mencari ingatan secara semantik
   mnemosyne_recall(query="Format laporan praktikum basis data dan nama dosen")
   ```

3. **Statistik Memori (`mnemosyne_stats`):**
   ```python
   # Memeriksa total memori tersimpan
   mnemosyne_stats()
   ```

### B. Hermes LCM Tools (Ingatan Konteks Panjang dalam Sesi)

1. **Pencarian Riwayat Sesi Mendalam (`lcm_grep`):**
   Mencari pesan atau potongan data teknis yang telah dikompresi berjam-jam lalu menggunakan pencarian FTS5 / hybrid.
   ```python
   lcm_grep(query="rumus kompleksitas binary search tree")
   ```

2. **Recall Semantik Sesi (`lcm_recall`):**
   Mengingat inti argumen atau keputusan desain yang pernah dibahas di awal sesi.
   ```python
   lcm_recall(query="alasan memilih arsitektur microservices untuk tugas besar")
   ```

3. **Status Mesin Kompresi (`lcm_status`):**
   Memeriksa rasio kompresi token obrolan saat ini.
   ```python
   lcm_status(reason="Periksa status kompresi token")
   ```

---

## 💡 Best Practices: Tiga Tingkat Retensi Memori Akademik

Untuk menjaga database memori tetap bersih dan bernilai tinggi, pandu agen Anda dengan aturan:
1. **Tier 1 (Fakta Statis - Importance 0.8–1.0):** Identitas mahasiswa, NIM, Jurusan, Dosen PA, Kurikulum. *Jarang berubah*.
2. **Tier 2 (Relasi & Progress - Importance 0.5–0.7):** Pembagian kelompok tugas, progres bab skripsi yang telah di-ACC, deadline ujian terdekat.
3. **Tier 3 (Prosedur & Preferensi - Importance 0.3–0.6):** Catatan koreksi dosen pengampu, preferensi bahasa, jadwal rutin mingguan.
4. **Sampah Sementara (Dilarang Disimpan ke Mnemosyne):** Basa-basi obrolan harian, data mentah ratusan baris, teks token sementara. Biarkan data ini dikelola secara efisien oleh Hermes LCM.

---

## 🛠️ Pemecahan Masalah (Troubleshooting)

* **Error: `Dimension mismatch in vector store`:**
  Pastikan nilai `LCM_EMBEDDING_STORE_DIM` sama persis dengan output dimensi embedding model yang Anda gunakan (contoh: 1536 untuk OpenAI `text-embedding-3-small`).
* **Error: `Connection refused on CDP / Embeddings`:**
  Periksa apakah endpoint API embedding dapat diakses melalui `curl https://api.openai.com/v1/models -H "Authorization: Bearer sk-..."`.
* **Memori tidak muncul setelah restart:**
  Pastikan opsi `hermes config set memory.memory_enabled true` sudah bernilai `true` dan database `~/.hermes/mnemosyne/data/mnemosyne.db` memiliki hak akses tulis (*write permissions*).
