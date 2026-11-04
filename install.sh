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
echo "📦 1/6. Menyalin 13 skill akademik ke $HERMES_SKILLS_DIR..."
cp -r "$REPO_DIR/skills/"* "$HERMES_SKILLS_DIR/"

# 2b. Siapkan service helper
mkdir -p "$HERMES_DIR/mendeley"
cp "$REPO_DIR/skills/academic-reference-manager/scripts/mendeley_service.py" "$HERMES_DIR/mendeley/mendeley_service.py" 2>/dev/null || true
chmod +x "$HERMES_DIR/mendeley/mendeley_service.py" 2>/dev/null || true

# 2c. Siapkan kredensial default Google Workspace jika belum ada
if [ ! -f "$HERMES_DIR/google_client_secret.json" ] && [ -f "$REPO_DIR/skills/academic-google-workspace/credentials/google_client_secret.json" ]; then
    echo "🔑 Menyalin default Google Workspace client_secret.json ke ~/.hermes/..."
    cp "$REPO_DIR/skills/academic-google-workspace/credentials/google_client_secret.json" "$HERMES_DIR/google_client_secret.json"
    chmod 600 "$HERMES_DIR/google_client_secret.json" 2>/dev/null || true
fi

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

# Pastikan Go compiler terpasang
if ! command -v go &>/dev/null; then
    echo "   Compiler Go belum terdeteksi. Menginstal Go secara otomatis..."
    if command -v apt-get &>/dev/null && [ "$(id -u)" -eq 0 ]; then
        apt-get update && apt-get install -y golang-go 2>/dev/null || true
    elif command -v sudo &>/dev/null && sudo -n true 2>/dev/null; then
        sudo apt-get update && sudo apt-get install -y golang-go 2>/dev/null || true
    else
        # Unduh Go binary tarball resmi ke ~/.local/go jika tanpa sudo
        GO_VER="1.22.5"
        echo "   Mengunduh Go v${GO_VER} binary ke ~/.local/go..."
        mkdir -p "$HOME/.local"
        curl -fsSL "https://go.dev/dl/go${GO_VER}.linux-amd64.tar.gz" 2>/dev/null | tar -C "$HOME/.local" -xz 2>/dev/null || true
        export PATH="$HOME/.local/go/bin:$PATH"
    fi
fi

if [ -d "$WAMEOW_DIR" ] && [ ! -f "$WAMEOW_DIR/wameow" ]; then
    if command -v go &>/dev/null; then
        echo "   Membangun binary wameow dari source Go..."
        (cd "$WAMEOW_DIR" && go build -o wameow .) || true
    else
        echo "   ⚠️ Gagal memasang Go otomatis. Silakan install manual: 'sudo apt install golang-go'."
    fi
fi

# 8. Setup WhatsApp Keep-Alive Heartbeat Ping
echo ""
echo "⏰ 5/6. Mengonfigurasi WhatsApp Keep-Alive Heartbeat Ping..."
python3 "$REPO_DIR/skills/unesa-wameow-bridge/scripts/setup_keepalive.py" --auto 2>/dev/null || true

# 9. Setup Google Workspace Dependencies
echo ""
echo "🌐 6/6. Memeriksa Google Workspace Library..."
if ! $TARGET_PYTHON -c "import googleapiclient" 2>/dev/null; then
    echo "   Menginstal google-api-python-client & google-auth..."
    $TARGET_PYTHON -m pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 2>/dev/null || pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 2>/dev/null || true
fi

# 10. Jalankan Pengecekan Realitas (Reality-Check Verification)
echo ""
python3 "$REPO_DIR/scripts/verify_setup.py"

echo "================================================================="
echo "🎉 Instalasi Selesai! Semua komponen telah disiapkan."
echo "================================================================="
