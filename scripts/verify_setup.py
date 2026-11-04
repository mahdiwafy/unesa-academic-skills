#!/usr/bin/env python3
"""
Diagnostic & Verification Script: UNESA Academic Skill Pack
Checks real environment status for:
- Academic Skills installation
- Wameow WhatsApp AI Bridge service & connection
- Mnemosyne Long-Term Memory
- Hermes LCM (Long Context Memory)
- WhatsApp Keep-Alive Ping Cronjob
- Local Credential Storage directory

Usage:
    python3 scripts/verify_setup.py [--json]
"""

import os
import sys
import json
import sqlite3
import argparse
import subprocess
import urllib.request
import urllib.error

HOME = os.path.expanduser("~")
HERMES_DIR = os.path.join(HOME, ".hermes")
SKILLS_DIR = os.path.join(HERMES_DIR, "skills", "academic")
CREDENTIALS_DIR = os.path.join(HERMES_DIR, "credentials")
WAMEOW_URL = os.environ.get("WAMEOW_BASE_URL", "http://localhost:52135")


def check_academic_skills():
    required_skills = [
        "unesa-academic-standards",
        "academic-life-schedule",
        "academic-reference-manager",
        "academic-forms-automation",
        "academic-memory-engine",
        "unesa-wameow-bridge",
        "unesa-office-engine",
        "unesa-communication-hub",
        "academic-presentation-mastery",
        "lab-and-coding-practical",
        "smart-study-and-research",
        "unesa-portal-guide",
        "academic-google-workspace",
    ]
    if not os.path.isdir(SKILLS_DIR):
        return {"status": "FAIL", "installed": 0, "total": len(required_skills), "missing": required_skills}

    found = []
    missing = []
    for s in required_skills:
        skill_path = os.path.join(SKILLS_DIR, s, "SKILL.md")
        if os.path.isfile(skill_path):
            found.append(s)
        else:
            # Also check alternative folder layout
            alt_path = os.path.join(HERMES_DIR, "skills", s, "SKILL.md")
            if os.path.isfile(alt_path):
                found.append(s)
            else:
                missing.append(s)

    status = "OK" if len(missing) == 0 else ("PARTIAL" if len(found) > 0 else "FAIL")
    return {"status": status, "installed": len(found), "total": len(required_skills), "missing": missing}


def check_wameow():
    # 1. Check HTTP API
    connected_sessions = []
    all_sessions = []
    api_online = False
    qr_needed = []

    try:
        req = urllib.request.Request(f"{WAMEOW_URL}/sessions", headers={"User-Agent": "Diagnostic"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            api_online = True
            for item in data:
                s_name = item.get("name", "")
                all_sessions.append(s_name)
                if item.get("status") == "connected":
                    connected_sessions.append(s_name)
                elif item.get("status") in ["qr", "qr_active", "disconnected"]:
                    qr_needed.append(s_name)
    except Exception:
        pass

    # 2. Check binary & process
    wameow_bin = os.path.join(HOME, "wameow", "wameow")
    bin_exists = os.path.isfile(wameow_bin)

    service_active = False
    try:
        res = subprocess.run(["systemctl", "is-active", "wameow"], capture_output=True, text=True, timeout=2)
        service_active = (res.stdout.strip() == "active")
    except Exception:
        pass

    # 3. Check SQLite DB
    db_path = os.path.join(HOME, "wameow", "wameow.db")
    db_exists = os.path.isfile(db_path)

    if api_online and len(connected_sessions) > 0:
        status = "OK"
        detail = f"Online on {WAMEOW_URL} (Sessions Connected: {', '.join(connected_sessions)})"
    elif api_online:
        status = "NEEDS_QR"
        detail = f"Service Online, but sessions require QR scan: {', '.join(qr_needed or all_sessions)}"
    elif bin_exists and service_active:
        status = "PORT_UNREACHABLE"
        detail = f"Binary exists, service active, but port 52135 not responding"
    elif bin_exists:
        status = "STOPPED"
        detail = f"Binary built at ~/wameow/wameow, but service is not running"
    else:
        status = "NOT_INSTALLED"
        detail = "Wameow binary not found at ~/wameow/wameow"

    return {
        "status": status,
        "api_online": api_online,
        "detail": detail,
        "connected_sessions": connected_sessions,
        "all_sessions": all_sessions,
        "db_exists": db_exists,
        "binary_exists": bin_exists,
    }


def check_mnemosyne():
    # Check python package
    pkg_installed = False
    try:
        import mnemosyne  # noqa
        pkg_installed = True
    except ImportError:
        # Check hermes agent venv if exists
        venv_py = os.path.join(HERMES_DIR, "hermes-agent", "venv", "bin", "python")
        if os.path.isfile(venv_py):
            res = subprocess.run([venv_py, "-c", "import mnemosyne; print('OK')"], capture_output=True, text=True)
            pkg_installed = ("OK" in res.stdout)

    # Check database
    db_paths = [
        os.path.join(HERMES_DIR, "mnemosyne", "data", "mnemosyne.db"),
        os.path.join(HERMES_DIR, "mnemosyne.db"),
        os.path.join(HERMES_DIR, "memory", "mnemosyne.db"),
    ]
    db_found = None
    count = 0
    for p in db_paths:
        if os.path.isfile(p):
            try:
                conn = sqlite3.connect(p)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM working_memory")
                count = cur.fetchone()[0]
                conn.close()
                db_found = p
                break
            except Exception:
                continue

    # Check mnemosyne plugin / tools
    plugin_dir = os.path.join(HERMES_DIR, "plugins", "hermes-mnemosyne")
    plugin_found = os.path.isdir(plugin_dir) or os.path.isdir(os.path.join(HERMES_DIR, "plugins", "mnemosyne"))

    if (pkg_installed or plugin_found) and db_found and count > 0:
        status = "OK"
        detail = f"Active ({count} memories stored in {os.path.basename(db_found)})"
    elif pkg_installed or plugin_found or db_found:
        status = "PARTIAL"
        detail = f"Installed (DB: {bool(db_found)}, Plugin: {plugin_found})"
    else:
        status = "NOT_INSTALLED"
        detail = "Package mnemosyne-memory not installed and no DB found"

    return {
        "status": status,
        "package_installed": pkg_installed,
        "db_path": db_found,
        "memory_count": count,
        "plugin_found": plugin_found,
        "detail": detail,
    }


def check_lcm():
    lcm_plugin_dir = os.path.join(HERMES_DIR, "plugins", "hermes-lcm")
    plugin_exists = os.path.isdir(lcm_plugin_dir)

    lcm_db = os.path.join(HERMES_DIR, "lcm.db")
    db_exists = os.path.isfile(lcm_db)

    config_file = os.path.join(HERMES_DIR, "config.yaml")
    compression_enabled = False
    if os.path.isfile(config_file):
        try:
            with open(config_file, "r") as f:
                content = f.read()
                if "compression:" in content and "enabled: true" in content:
                    compression_enabled = True
        except Exception:
            pass

    if plugin_exists and compression_enabled:
        status = "OK"
        detail = "Plugin installed and compression enabled in config.yaml"
    elif plugin_exists:
        status = "PARTIAL"
        detail = "Plugin folder exists, but compression not enabled in config.yaml"
    elif db_exists:
        status = "PARTIAL"
        detail = "lcm.db exists, but plugin folder not found"
    else:
        status = "NOT_INSTALLED"
        detail = "Hermes LCM plugin not found in ~/.hermes/plugins/hermes-lcm"

    return {
        "status": status,
        "plugin_exists": plugin_exists,
        "db_exists": db_exists,
        "compression_enabled": compression_enabled,
        "detail": detail,
    }


def check_keepalive_cron():
    jobs_file = os.path.join(HERMES_DIR, "cron", "jobs.json")
    cron_found = False
    cron_detail = "Belum terpasang"
    ping_script = os.path.join(HERMES_DIR, "scripts", "wameow-ping.sh")
    script_exists = os.path.isfile(ping_script)

    if os.path.isfile(jobs_file):
        try:
            with open(jobs_file, "r") as f:
                data = json.load(f)
            jobs = data.get("jobs", data)
            if isinstance(jobs, dict):
                jobs = jobs.values()
            for j in jobs:
                if not isinstance(j, dict):
                    continue
                cmd = (j.get("name", "") + " " + j.get("prompt", "") + " " + j.get("script", "")).lower()
                if "ping" in cmd or "wameow-ping" in cmd:
                    cron_found = True
                    cron_detail = f"Hermes cron active: {j.get('name')} ({j.get('schedule_display', j.get('schedule', ''))})"
                    break
        except Exception:
            pass

    # Check system crontab as fallback
    if not cron_found:
        try:
            res = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=2)
            if "ping" in res.stdout.lower() or "wameow" in res.stdout.lower():
                cron_found = True
                cron_detail = "Linux system crontab active"
        except Exception:
            pass

    status = "OK" if cron_found else ("PARTIAL" if script_exists else "NOT_CONFIGURED")
    return {
        "status": status,
        "cron_found": cron_found,
        "script_exists": script_exists,
        "detail": cron_detail,
    }


def check_google_workspace():
    secret_paths = [
        os.path.join(HERMES_DIR, "google_client_secret.json"),
        os.path.join(HERMES_DIR, "skills", "academic", "academic-google-workspace", "credentials", "google_client_secret.json"),
    ]
    secret_exists = any(os.path.isfile(p) for p in secret_paths)

    tokens = []
    for f in ["google_token_personal.json", "google_token_sso.json", "google_token.json"]:
        p = os.path.join(HERMES_DIR, f)
        if os.path.isfile(p):
            try:
                with open(p) as tf:
                    td = json.load(tf)
                if td.get("token") or td.get("refresh_token"):
                    tokens.append(f.replace("google_token_", "").replace(".json", ""))
            except Exception:
                pass

    if secret_exists and len(tokens) > 0:
        status = "OK"
        detail = f"Connected ({', '.join(tokens)}) via project credentials"
    elif secret_exists:
        status = "NEEDS_AUTH"
        detail = "Client credentials ready. Run setup_google.py --auth-url to login."
    else:
        status = "NOT_INSTALLED"
        detail = "Kredensial Google Workspace belum terpasang."

    return {
        "status": status,
        "secret_exists": secret_exists,
        "connected_accounts": tokens,
        "detail": detail,
    }


def check_credentials_dir():
    exists = os.path.isdir(CREDENTIALS_DIR)
    file_count = len(os.listdir(CREDENTIALS_DIR)) if exists else 0
    return {
        "status": "OK" if exists else "NOT_CREATED",
        "path": CREDENTIALS_DIR,
        "file_count": file_count,
        "detail": f"{file_count} credentials stored locally" if exists else "Direktori ~/.hermes/credentials belum dibuat",
    }


def main():
    parser = argparse.ArgumentParser(description="Verify UNESA Academic Skill Pack Setup")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    skills = check_academic_skills()
    wameow = check_wameow()
    mnemosyne = check_mnemosyne()
    lcm = check_lcm()
    cron = check_keepalive_cron()
    gws = check_google_workspace()
    creds = check_credentials_dir()

    results = {
        "academic_skills": skills,
        "wameow_bridge": wameow,
        "mnemosyne_memory": mnemosyne,
        "hermes_lcm": lcm,
        "whatsapp_keepalive_cron": cron,
        "google_workspace": gws,
        "credentials_storage": creds,
    }

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print("\n" + "=" * 65)
    print("🎓 UNESA ACADEMIC SKILL PACK — REALITY CHECK & SYSTEM STATUS")
    print("=" * 65)

    def icon(status):
        if status == "OK":
            return "✅ [PASS]"
        elif status in ["PARTIAL", "NEEDS_QR", "PORT_UNREACHABLE", "STOPPED", "NEEDS_AUTH"]:
            return "⚠️  [WARN]"
        else:
            return "❌ [FAIL]"

    print(f"{icon(skills['status'])} Academic Skills        : {skills['installed']}/{skills['total']} skills installed in ~/.hermes/skills/academic")
    print(f"{icon(gws['status'])} Google Workspace (Suite): {gws['detail']}")
    print(f"{icon(wameow['status'])} Wameow WhatsApp Bridge : {wameow['detail']}")
    print(f"{icon(mnemosyne['status'])} Mnemosyne Memory       : {mnemosyne['detail']}")
    print(f"{icon(lcm['status'])} Hermes LCM (Context)    : {lcm['detail']}")
    print(f"{icon(cron['status'])} WhatsApp KeepAlive Cron : {cron['detail']}")
    print(f"{icon(creds['status'])} Local Credentials Dir  : {creds['detail']}")
    print("-" * 65)

    # Reality Check Summary for AI Agents
    print("\n💡 PANDUAN UNTUK AI AGENT (ZERO-HALLUCINATION DIRECTIVE):")
    all_ok = all(r["status"] == "OK" for r in [skills, wameow, mnemosyne, lcm, cron, gws])
    if all_ok:
        print("  Semua komponen terverifikasi AKTIF secara nyata. Anda dapat melayani")
        print("  pengguna secara penuh tanpa halusinasi.")
    else:
        print("  PERHATIAN: Ada komponen yang BELUM AKTIF atau BELUM TERPASANG.")
        print("  DILARANG KERAS memberi tahu pengguna bahwa komponen di atas sudah aktif")
        print("  jika statusnya masih [WARN] atau [FAIL]!")
        print("  Tawarkan kepada pengguna untuk menjalankan instalasi lengkap:")
        print("    bash install.sh --full")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
