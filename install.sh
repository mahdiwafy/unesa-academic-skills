#!/usr/bin/env bash
# ==============================================================================
# Installer Script: UNESA Academic Skill Pack for Hermes Agent & AI Coding Tools
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_SKILLS_DIR="$HOME/.hermes/skills/academic"
HERMES_SOUL_PATH="$HOME/.hermes/SOUL.md"

echo "🎓 Memulai instalasi UNESA Academic Skill Pack..."

# 1. Pastikan folder tujuan di Hermes ada
mkdir -p "$HERMES_SKILLS_DIR"

# 2. Salin seluruh skill ke direktori Hermes
echo "📦 Menyalin skill ke $HERMES_SKILLS_DIR..."
cp -r "$REPO_DIR/skills/"* "$HERMES_SKILLS_DIR/"

# 3. Beri permission execute pada script pembantu jika ada
find "$HERMES_SKILLS_DIR" -name "*.py" -exec chmod +x {} + 2>/dev/null || true
find "$HERMES_SKILLS_DIR" -name "*.sh" -exec chmod +x {} + 2>/dev/null || true

# 4. Opsional: Pasang SOUL.md jika belum ada atau user ingin menggunakannya
if [ ! -f "$HERMES_SOUL_PATH" ]; then
    echo "✨ Menyiapkan SOUL.md akademik default di $HERMES_SOUL_PATH..."
    cp "$REPO_DIR/SOUL_TEMPLATE.md" "$HERMES_SOUL_PATH"
else
    echo "ℹ️  SOUL.md yang sudah ada di $HERMES_SOUL_PATH dipertahankan."
    echo "   (Lihat '$REPO_DIR/SOUL_TEMPLATE.md' jika ingin menggabungkan persona akademik)."
fi

# 5. Opsional: Cek apakah officecli terinstall di laptop/mesin
if ! command -v officecli &> /dev/null; then
    echo ""
    echo "💡 Tips: Anda dapat menginstal officecli untuk manipulasi file Word/Excel/PPT di laptop tanpa MS Office:"
    echo "   curl -fsSL https://d.officecli.ai/install.sh | bash  (Linux/macOS)"
    echo "   irm https://d.officecli.ai/install.ps1 | iex         (Windows PowerShell)"
fi

echo ""
echo "✅ Instalasi Berhasil!"
echo "--------------------------------------------------"
echo "Skill yang terpasang di Hermes Agent:"
echo "  1. unesa-academic-standards    - Format Makalah/Skripsi/DOCX"
echo "  2. unesa-office-engine         - Manipulasi Word, Excel & PPT di Laptop (officecli)"
echo "  3. unesa-wameow-bridge         - Integrasi WhatsApp AI Anti-Banned (whatsmeow)"
echo "  4. unesa-communication-hub      - Chat Dosen & Broadcast Komti"
echo "  5. academic-presentation-mastery - Slide & Speaker Notes"
echo "  6. lab-and-coding-practical    - Laporan Praktikum & Clean Code"
echo "  7. smart-study-and-research    - Bedah Jurnal & Bank Soal UTS/UAS"
echo "  8. unesa-portal-guide          - Panduan Siakadu, Vinesa, SiDia, TEP"
echo "--------------------------------------------------"
echo "💡 Jalankan 'hermes' dan panggil skill kapan pun kamu butuh bantuan akademik!"
