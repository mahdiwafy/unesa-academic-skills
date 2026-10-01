#!/usr/bin/env bash
# ==============================================================================
# Installer Script: UNESA Academic Skill Pack for Hermes Agent & AI Coding Tools
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_SKILLS_DIR="$HOME/.hermes/skills/academic"

echo "🎓 Memulai instalasi UNESA Academic Skill Pack..."

# 1. Pastikan folder tujuan di Hermes ada
mkdir -p "$HERMES_SKILLS_DIR"

# 2. Salin seluruh skill ke direktori Hermes
echo "📦 Menyalin skill ke $HERMES_SKILLS_DIR..."
cp -r "$REPO_DIR/skills/"* "$HERMES_SKILLS_DIR/"

# 3. Beri permission execute pada script pembantu jika ada
find "$HERMES_SKILLS_DIR" -name "*.py" -exec chmod +x {} + 2>/dev/null || true
find "$HERMES_SKILLS_DIR" -name "*.sh" -exec chmod +x {} + 2>/dev/null || true

echo ""
echo "✅ Instalasi Berhasil!"
echo "--------------------------------------------------"
echo "Skill yang terpasang di Hermes Agent:"
echo "  1. unesa-academic-standards  - Format Makalah/Skripsi/DOCX"
echo "  2. unesa-communication-hub    - Chat Dosen & Broadcast Komti"
echo "  3. academic-presentation-mastery - Slide & Speaker Notes"
echo "  4. lab-and-coding-practical  - Laporan Praktikum & Clean Code"
echo "  5. smart-study-and-research  - Bedah Jurnal & Bank Soal UTS/UAS"
echo "  6. unesa-portal-guide        - Panduan Siakadu, Vinesa, SiDia, TEP"
echo "--------------------------------------------------"
echo "💡 Jalankan 'hermes' dan panggil skill kapan pun kamu butuh bantuan akademik!"
