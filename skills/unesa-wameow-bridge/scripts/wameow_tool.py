#!/usr/bin/env python3
"""
Wameow CLI Tool for AI Agents (wameow_tool.py)
A lightweight helper script to interact with Wameow WhatsApp AI Bridge.

Supports:
- Checking connection status & QR pairing
- Sending asynchronous text messages (with anti-ban typing simulation)
- Uploading academic files (Word, Excel, PowerPoint, PDF, images)
- Searching message history & contacts
"""

import sys
import os
import re
import json
import argparse
import mimetypes
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional

DEFAULT_BASE_URL = os.environ.get("WAMEOW_BASE_URL", "http://localhost:52135")
DEFAULT_SESSION = os.environ.get("WAMEOW_SESSION", "wa1")


def normalize_phone(phone: str) -> str:
    """Normalize phone number to international WhatsApp format without '+' or non-digit chars."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("08"):
        digits = "628" + digits[2:]
    elif digits.startswith("8"):
        digits = "628" + digits[1:]
    return digits


def make_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}{endpoint}"
    headers = {"User-Agent": "Wameow-Agent-Client/1.0"}

    req_data = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        req_data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
            try:
                return json.loads(content)
            except Exception:
                return {"status_code": resp.status, "raw_response": content}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        try:
            return {"error": True, "status_code": e.code, "message": json.loads(err_msg)}
        except Exception:
            return {"error": True, "status_code": e.code, "message": err_msg}
    except Exception as e:
        return {"error": True, "message": str(e)}


def check_status(session: str = DEFAULT_SESSION, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    return make_request("GET", f"/qr/{session}", base_url=base_url)


def send_message(phone: str, text: str, session: str = DEFAULT_SESSION, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    clean_phone = normalize_phone(phone)
    payload = {
        "session": session,
        "chatId": clean_phone,
        "text": text,
    }
    return make_request("POST", "/send-async", data=payload, base_url=base_url)


def send_file(
    phone: str,
    file_path: str,
    caption: str = "",
    filename: Optional[str] = None,
    session: str = DEFAULT_SESSION,
    base_url: str = DEFAULT_BASE_URL,
) -> Dict[str, Any]:
    abs_path = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.exists(abs_path):
        return {"error": True, "message": f"Berkas tidak ditemukan di path: {abs_path}"}

    clean_phone = normalize_phone(phone)
    actual_filename = filename or os.path.basename(abs_path)

    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(abs_path)
    if not mime_type:
        ext = os.path.splitext(abs_path)[1].lower()
        mime_map = {
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".pdf": "application/pdf",
            ".zip": "application/zip",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    payload = {
        "session": session,
        "chatId": clean_phone,
        "filePath": abs_path,
        "fileName": actual_filename,
        "caption": caption,
        "mimetype": mime_type,
    }
    return make_request("POST", "/send-media", data=payload, base_url=base_url)


def search_messages(query: str, session: str = DEFAULT_SESSION, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    encoded_q = urllib.parse.quote(query)
    return make_request("GET", f"/history/search?q={encoded_q}&session={session}", base_url=base_url)


def main():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--session", default=DEFAULT_SESSION, help=f"Nama session WhatsApp (default: {DEFAULT_SESSION})")
    parent_parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Base URL Wameow (default: {DEFAULT_BASE_URL})")

    parser = argparse.ArgumentParser(
        description="Wameow WhatsApp AI Bridge CLI Helper for Agents",
        parents=[parent_parser]
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. status
    subparsers.add_parser("status", parents=[parent_parser], help="Periksa status koneksi session WhatsApp")

    # 2. send
    send_parser = subparsers.add_parser("send", parents=[parent_parser], help="Kirim pesan teks asinkron (aman anti-banned)")
    send_parser.add_argument("phone", help="Nomor tujuan (contoh: 081234567890 atau 6281234567890)")
    send_parser.add_argument("text", help="Isi pesan teks yang ingin dikirim")

    # 3. send-file
    file_parser = subparsers.add_parser("send-file", parents=[parent_parser], help="Kirim berkas dokumen/media (DOCX, PDF, PPTX, gambar)")
    file_parser.add_argument("phone", help="Nomor tujuan")
    file_parser.add_argument("file_path", help="Path absolut atau relatif ke berkas")
    file_parser.add_argument("--caption", default="", help="Teks pesan pengantar/keterangan berkas")
    file_parser.add_argument("--filename", default=None, help="Nama berkas kustom saat diterima lawan bicara")

    # 4. search
    search_parser = subparsers.add_parser("search", parents=[parent_parser], help="Cari pesan di riwayat chat berdasarkan kata kunci")
    search_parser.add_argument("query", help="Kata kunci pencarian")

    args = parser.parse_args()

    if args.command == "status":
        res = check_status(session=args.session, base_url=args.base_url)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        if res.get("status") == "connected":
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.command == "send":
        res = send_message(args.phone, args.text, session=args.session, base_url=args.base_url)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "send-file":
        res = send_file(
            args.phone,
            args.file_path,
            caption=args.caption,
            filename=args.filename,
            session=args.session,
            base_url=args.base_url,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "search":
        res = search_messages(args.query, session=args.session, base_url=args.base_url)
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
