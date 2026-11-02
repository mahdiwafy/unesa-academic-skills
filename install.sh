#!/usr/bin/env bash
# ==============================================================================
# Installer & Bootstrap Script: UNESA Academic Skill Pack
# Supports:
#   bash install.sh          -> Interactive / Comprehensive Autonomous Setup
#   bash install.sh --full   -> Full Installation (Skills + Wameow + Mnemosyne + LCM + KeepAlive)
#   bash install.sh --quick  -> Skills-only quick install
#   bash install.sh --verify -> Run diagnostic verification check only
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_DIR="$HOME/.hermes"
HERMES_SKILLS_DIR="$HERMES_DIR/skills/academic"
HERMES_SOUL_PATH="$HERMES_DIR/SOUL.md"
CREDENTIALS_DIR="$HERMES_DIR/credentials"
SCRIPTS_DIR="$HERMES_DIR/scripts"

MODE="full"
for arg in "$@"; do
  case $arg in
    --quick) MODE="quick" ;;
    --verify) MODE="verify" ;;
    --full|--all) MODE="full" ;;
  esac
done

if [ "$MODE" = "verify" ]; then
    python3 "$REPO_DIR/scripts/verify_setup.py"
    exit 0
fi

echo "================================================================="
echo "🎓 UNESA ACADEMIC SKILL PACK — AUTONOMOUS INSTALLER"
echo "================================================================="
echo "Mode: $MODE"
echo ""

# 1. Pastikan folder-folder esensial di Hermes ada
mkdir -p "$HERMES_SKILLS_DIR"
mkdir -p "$CREDENTIALS_DIR"
mkdir -p "$SCRIPTS_DIR"

# 2. Salin seluruh skill ke direktori Hermes
echo "📦 1/5. Menyalin 12 skill akademik ke $HERMES_SKILLS_DIR..."
cp -r "$REPO_DIR/skills/"* "$HERMES_SKILLS_DIR/"

# 2b. Siapkan service helper
mkdir -p "$HERMES_DIR/mendeley"
cp "$REPO_DIR/skills/academic-reference-manager/scripts/mendeley_service.py" "$HERMES_DIR/mendeley/mendeley_service.py" 2>/dev/null || true
chmod +x "$HERMES_DIR/mendeley/mendeley_service.py" 2>/dev/null || true

# 3. Beri permission execute pada script pembantu
find "$HERMES_SKILLS_DIR" -name "*.py" -exec chmod +x {} + 2>/dev/null || true
find "$HERMES_SKILLS_DIR" -name "*.sh" -exec chmod +x {} + 2>/dev/null || true
chmod +x "$REPO_DIR/scripts/"*.py 2>/dev/null || true

# 4. Siapkan SOUL.md akademik default jika belum ada
if [ ! -f "$HERMES_SOUL_PATH" ]; then
    echo "✨ Menyiapkan SOUL.md akademik default di $HERMES_SOUL_PATH..."
    cp "$REPO_DIR/SOUL_TEMPLATE.md" "$HERMES_SOUL_PATH"
else
    echo "ℹ️  SOUL.md sudah ada di $HERMES_SOUL_PATH (dipertahankan)."
fi

# Jika mode quick, langsung lompat ke akhir
if [ "$MODE" = "quick" ]; then
    echo "✅ Mode quick selesai!"
    python3 "$REPO_DIR/scripts/verify_setup.py"
    exit 0
fi

# ==============================================================================
# FULL INSTALLATION: ENGINE SETUP (MNEMOSYNE, LCM, WAMEOW, KEEPALIVE)
# ==============================================================================

# 5. Setup Mnemosyne Long-Term Memory
echo ""
echo "🧠 2/5. Memeriksa & Mengonfigurasi Mnemosyne Memory..."
VENV_PYTHON="$HERMES_DIR/hermes-agent/venv/bin/python"
TARGET_PYTHON="python3"
if [ -f "$VENV_PYTHON" ]; then
    TARGET_PYTHON="$VENV_PYTHON"
fi

if ! $TARGET_PYTHON -c "import mnemosyne" 2>/dev/null; then
    echo "   Menginstal package mnemosyne-memory & mnemosyne-hermes via pip..."
    $TARGET_PYTHON -m pip install --upgrade mnemosyne-memory mnemosyne-hermes 2>/dev/null || pip install --upgrade mnemosyne-memory mnemosyne-hermes 2>/dev/null || true
fi

if command -v hermes &>/dev/null; then
    hermes config set memory.provider mnemosyne 2>/dev/null || true
    hermes config set memory.memory_enabled true 2>/dev/null || true
fi

# 6. Setup Hermes LCM (Long Context Memory)
echo ""
echo "🗜️  3/5. Memeriksa & Mengonfigurasi Hermes LCM (Context Compression)..."
LCM_PLUGIN_DIR="$HERMES_DIR/plugins/hermes-lcm"
if [ ! -d "$LCM_PLUGIN_DIR" ]; then
    echo "   Mengunduh plugin hermes-lcm dari GitHub..."
    mkdir -p "$HERMES_DIR/plugins"
    git clone https://github.com/NousResearch/hermes-lcm "$LCM_PLUGIN_DIR" 2>/dev/null || true
    if [ -f "$LCM_PLUGIN_DIR/requirements.txt" ]; then
        $TARGET_PYTHON -m pip install -r "$LCM_PLUGIN_DIR/requirements.txt" 2>/dev/null || true
    fi
fi

if command -v hermes &>/dev/null; then
    hermes config set compression.enabled true 2>/dev/null || true
fi

# 7. Setup Wameow WhatsApp AI Bridge
echo ""
echo "📱 4/5. Memeriksa Wameow WhatsApp AI Bridge..."
WAMEOW_DIR="$HOME/wameow"
if [ ! -d "$WAMEOW_DIR" ]; then
    echo "   Meng-clone repositori Wameow ke ~/wameow..."
    git clone https://github.com/mahdiwafy/wameow.git "$WAMEOW_DIR" 2>/dev/null || true
fi

if [ -d "$WAMEOW_DIR" ] && [ ! -f "$WAMEOW_DIR/wameow" ]; then
    if command -v go &>/dev/null; then
        echo "   Membangun binary wameow dari source Go..."
        (cd "$WAMEOW_DIR" && go build -o wameow .) || true
    else
        echo "   ⚠️ Go belum terinstall. Silakan install Go ('sudo apt install golang-go') untuk build wameow."
    fi
fi

# 8. Setup WhatsApp Keep-Alive Heartbeat Ping
echo ""
echo "⏰ 5/5. Mengonfigurasi WhatsApp Keep-Alive Heartbeat Ping..."
python3 "$REPO_DIR/skills/unesa-wameow-bridge/scripts/setup_keepalive.py" --auto 2>/dev/null || true

# 9. Jalankan Pengecekan Realitas (Reality-Check Verification)
echo ""
python3 "$REPO_DIR/scripts/verify_setup.py"

echo "================================================================="
echo "🎉 Instalasi Selesai! Semua komponen telah disiapkan."
echo "================================================================="
