#!/usr/bin/env python3
"""
Mendeley Reference Manager CLI Service
======================================
Modul CLI mandiri untuk mengelola pustaka referensi Mendeley via REST API.
Mendukung sinkronisasi dokumen, metadata sitasi, pencarian, dan unggah berkas PDF.
"""

import os
import sys
import json
import argparse
import urllib.parse
import requests

CREDENTIALS_FILE = os.path.expanduser("~/.hermes/credentials/mendeley.json")
TOKEN_FILE = os.path.expanduser("~/.hermes/credentials/mendeley_tokens.json")


def load_credentials():
    """Muat konfigurasi kredensial developer Mendeley."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"Kredensial Mendeley tidak ditemukan di '{CREDENTIALS_FILE}'.\n"
            "Silakan buat file tersebut berdasarkan panduan di docs/PANDUAN_SETUP_MENDELEY_API_DAN_OAUTH.md."
        )
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_auth_url():
    """Hasilkan URL otorisasi OAuth 2.0 untuk login Mendeley."""
    creds = load_credentials()
    params = {
        "client_id": creds["client_id"],
        "redirect_uri": creds.get("redirect_uri", "http://localhost:8080"),
        "response_type": "code",
        "scope": "all",
    }
    return "https://api.mendeley.com/oauth/authorize?" + urllib.parse.urlencode(params)


def exchange_code(code):
    """Tukar authorization code dengan access token dan refresh token."""
    creds = load_credentials()
    url = "https://api.mendeley.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "redirect_uri": creds.get("redirect_uri", "http://localhost:8080"),
        "code": code.strip(),
    }
    resp = requests.post(url, data=data, timeout=30)
    if resp.status_code == 200:
        tokens = resp.json()
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2)
        try:
            os.chmod(TOKEN_FILE, 0o600)
        except OSError:
            pass
        return tokens
    else:
        raise Exception(f"Gagal menukar kode otorisasi: HTTP {resp.status_code} - {resp.text}")


def refresh_access_token():
    """Perbarui access token menggunakan refresh token yang tersimpan."""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(f"File token tidak ditemukan di '{TOKEN_FILE}'. Silakan otorisasi terlebih dahulu.")

    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        tokens = json.load(f)

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise ValueError("Refresh token tidak tersedia di file token.")

    creds = load_credentials()
    url = "https://api.mendeley.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": refresh_token,
    }
    resp = requests.post(url, data=data, timeout=30)
    if resp.status_code == 200:
        new_tokens = resp.json()
        if "refresh_token" not in new_tokens and refresh_token:
            new_tokens["refresh_token"] = refresh_token
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(new_tokens, f, indent=2)
        return new_tokens.get("access_token")
    else:
        raise Exception(f"Gagal me-refresh token: HTTP {resp.status_code} - {resp.text}")


def get_headers(content_type=None, accept_type="application/vnd.mendeley-document.1+json", retry=True):
    """Bangun headers permintaan dengan access token aktif."""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("Mendeley belum diautentikasi. Jalankan perintah 'auth-url' dan 'auth-code'.")

    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        tokens = json.load(f)

    access_token = tokens.get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "MendeleyAcademicService/1.0",
    }
    if accept_type:
        headers["Accept"] = accept_type
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def authenticated_request(method, url, **kwargs):
    """Jalankan permintaan HTTP dengan auto-retry refresh token bila token kadaluarsa (HTTP 401)."""
    headers = kwargs.get("headers")
    resp = requests.request(method, url, **kwargs)
    if resp.status_code == 401:
        try:
            new_token = refresh_access_token()
            if headers and "Authorization" in headers:
                headers["Authorization"] = f"Bearer {new_token}"
            kwargs["headers"] = headers
            resp = requests.request(method, url, **kwargs)
        except Exception:
            pass
    return resp


def list_documents(limit=50):
    """Ambil daftar dokumen di perpustakaan Mendeley."""
    headers = get_headers()
    url = f"https://api.mendeley.com/documents?limit={limit}"
    resp = authenticated_request("GET", url, headers=headers, timeout=30)
    if resp.status_code == 200:
        return resp.json()
    return {"error": resp.status_code, "message": resp.text}


def add_document(title, doc_type="journal", authors=None, year=None, abstract=None, doi=None):
    """Tambahkan dokumen / metadata pustaka baru ke Mendeley."""
    headers = get_headers(content_type="application/vnd.mendeley-document.1+json")
    data = {
        "title": title,
        "type": doc_type,
    }
    if authors:
        data["authors"] = authors
    if year:
        data["year"] = int(year)
    if abstract:
        data["abstract"] = abstract
    if doi:
        data["identifiers"] = {"doi": doi}

    resp = authenticated_request("POST", "https://api.mendeley.com/documents", headers=headers, json=data, timeout=30)
    if resp.status_code == 201:
        return resp.json()
    return {"error": resp.status_code, "message": resp.text}


def upload_file(doc_id, file_path):
    """Unggah berkas PDF referensi ke dokumen Mendeley yang sudah dibuat."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Berkas tidak ditemukan: {file_path}")

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    headers = get_headers(content_type="application/pdf", accept_type="application/vnd.mendeley-file.1+json")
    headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    headers["Link"] = f'<https://api.mendeley.com/documents/{doc_id}>; rel="document"'

    resp = authenticated_request("POST", "https://api.mendeley.com/files", headers=headers, data=file_bytes, timeout=60)
    if resp.status_code == 201:
        return resp.json()
    return {"error": resp.status_code, "message": resp.text}


def search_documents(query):
    """Cari dokumen di perpustakaan berdasarkan judul, abstrak, atau penulis."""
    docs = list_documents(limit=100)
    if isinstance(docs, list):
        q = query.lower()
        matches = []
        for d in docs:
            title = d.get("title", "").lower()
            abstract = d.get("abstract", "").lower()
            authors_str = " ".join([f"{a.get('first_name', '')} {a.get('last_name', '')}" for a in d.get("authors", [])]).lower()
            if q in title or q in abstract or q in authors_str:
                matches.append(d)
        return matches
    return docs


def delete_document(doc_id):
    """Hapus dokumen dari perpustakaan Mendeley."""
    headers = get_headers()
    resp = authenticated_request("DELETE", f"https://api.mendeley.com/documents/{doc_id}", headers=headers, timeout=30)
    if resp.status_code == 204:
        return {"status": "success", "message": f"Dokumen {doc_id} berhasil dihapus."}
    return {"error": resp.status_code, "message": resp.text}


def main():
    parser = argparse.ArgumentParser(description="Mendeley Reference Manager Service")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("auth-url", help="Tampilkan URL otorisasi OAuth 2.0")

    auth_code_parser = subparsers.add_parser("auth-code", help="Tukar authorization code dengan token")
    auth_code_parser.add_argument("code", help="Kode otorisasi dari redirect URL")

    list_parser = subparsers.add_parser("list", help="Daftar dokumen referensi")
    list_parser.add_argument("--limit", type=int, default=50, help="Jumlah maksimum dokumen")

    add_parser = subparsers.add_parser("add", help="Tambah dokumen referensi baru")
    add_parser.add_argument("--title", required=True, help="Judul artikel / buku")
    add_parser.add_argument("--type", default="journal", help="Tipe dokumen (journal, book, conference_proceedings)")
    add_parser.add_argument("--year", type=int, help="Tahun publikasi")
    add_parser.add_argument("--abstract", help="Abstrak artikel")
    add_parser.add_argument("--doi", help="Digital Object Identifier (DOI)")
    add_parser.add_argument("--author", action="append", help="Penulis (Format: 'First Last' atau JSON)")

    upload_parser = subparsers.add_parser("upload-file", help="Unggah file PDF ke dokumen")
    upload_parser.add_argument("doc_id", help="ID Dokumen Mendeley")
    upload_parser.add_argument("file_path", help="Path berkas PDF lokal")

    search_parser = subparsers.add_parser("search", help="Cari dokumen di pustaka")
    search_parser.add_argument("query", help="Kata kunci pencarian")

    del_parser = subparsers.add_parser("delete", help="Hapus dokumen")
    del_parser.add_argument("id", help="ID Dokumen Mendeley")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "auth-url":
            print(get_auth_url())
        elif args.command == "auth-code":
            result = exchange_code(args.code)
            print(json.dumps({"status": "success", "message": "Otorisasi berhasil tersimpan!"}, indent=2))
        elif args.command == "list":
            print(json.dumps(list_documents(limit=args.limit), indent=2))
        elif args.command == "add":
            authors = None
            if args.author:
                authors = []
                for a in args.author:
                    parts = a.strip().rsplit(" ", 1)
                    if len(parts) == 2:
                        authors.append({"first_name": parts[0], "last_name": parts[1]})
                    else:
                        authors.append({"last_name": parts[0]})
            print(json.dumps(add_document(args.title, args.type, authors=authors, year=args.year, abstract=args.abstract, doi=args.doi), indent=2))
        elif args.command == "upload-file":
            print(json.dumps(upload_file(args.doc_id, args.file_path), indent=2))
        elif args.command == "search":
            print(json.dumps(search_documents(args.query), indent=2))
        elif args.command == "delete":
            print(json.dumps(delete_document(args.id), indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
