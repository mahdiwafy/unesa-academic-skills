#!/usr/bin/env python3
"""Unified Google Workspace CLI Tool for AI Agents (google_tool.py).

Supports:
- Google Sheets (Spreadsheet: read, update, append, create)
- Google Docs (read, create, append)
- Google Drive (search, upload, download, share, mkdir)
- Google Photos (list, albums, search, upload)
- Google Calendar & Tasks (events, deadlines)
- Google Classroom (courses, coursework, announcements)
- Gmail (search, send, draft)

Usage:
  python3 google_tool.py sheets get <sheet_id> [--range Sheet1!A1:D10]
  python3 google_tool.py sheets append <sheet_id> --values "Ahmad,26050974001,Hadir"
  python3 google_tool.py docs get <doc_id>
  python3 google_tool.py docs create --title "Draf Makalah" --text "Isi..."
  python3 google_tool.py drive search "Laporan Praktikum"
  python3 google_tool.py drive upload /path/to/file.pdf
  python3 google_tool.py photos list --max 10
  python3 google_tool.py calendar list --max 5
  python3 google_tool.py tasks list
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _hermes_home import get_hermes_home

HERMES_HOME = get_hermes_home()


def resolve_token_file(account: str | None = None) -> Path:
    act = (account or os.getenv("HERMES_GOOGLE_ACCOUNT") or "personal").lower()
    if act in ("sso", "unesa", "campus"):
        p = HERMES_HOME / "google_token_sso.json"
        if p.exists():
            return p
    p_personal = HERMES_HOME / "google_token_personal.json"
    if p_personal.exists():
        return p_personal
    return HERMES_HOME / "google_token.json"


def get_access_token(account: str | None = None) -> str:
    token_file = resolve_token_file(account)
    if not token_file.exists():
        raise FileNotFoundError(f"File token Google tidak ditemukan di {token_file}. Jalankan setup_google.py --auth-url.")

    with open(token_file, "r") as f:
        data = json.load(f)

    # Check refresh
    token = data.get("token")
    refresh_tok = data.get("refresh_token")
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")

    # If refresh_token exists, do refresh if needed
    if refresh_tok and client_id and client_secret:
        try:
            body = urllib.parse.urlencode({
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_tok,
                "grant_type": "refresh_token",
            }).encode()
            req = urllib.request.Request(data.get("token_uri", "https://oauth2.googleapis.com/token"), data=body, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                token = res.get("access_token", token)
                data["token"] = token
                with open(token_file, "w") as f:
                    json.dump(data, f, indent=2)
        except Exception:
            pass

    return token


def api_request(method: str, url: str, data: dict | list | None = None, account: str | None = None) -> dict:
    token = get_access_token(account)
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "UNESA-Academic-Hermes/1.0",
    }
    body_bytes = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body_bytes = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {"status": "ok"}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            return {"error": True, "code": e.code, "detail": json.loads(err_body)}
        except Exception:
            return {"error": True, "code": e.code, "detail": err_body}
    except Exception as e:
        return {"error": True, "detail": str(e)}


# --- Google Sheets ---
def sheets_get(args):
    range_param = urllib.parse.quote(args.range) if args.range else "Sheet1!A1:Z100"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{args.sheet_id}/values/{range_param}"
    res = api_request("GET", url, account=args.account)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def sheets_append(args):
    range_param = urllib.parse.quote(args.range or "Sheet1!A1")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{args.sheet_id}/values/{range_param}:append?valueInputOption=USER_ENTERED"
    vals = [v.strip() for v in args.values.split(",")]
    payload = {"values": [vals]}
    res = api_request("POST", url, data=payload, account=args.account)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def sheets_create(args):
    url = "https://sheets.googleapis.com/v4/spreadsheets"
    payload = {"properties": {"title": args.title}}
    res = api_request("POST", url, data=payload, account=args.account)
    print(json.dumps(res, indent=2, ensure_ascii=False))


# --- Google Docs ---
def docs_get(args):
    url = f"https://docs.googleapis.com/v1/documents/{args.doc_id}"
    res = api_request("GET", url, account=args.account)
    if "error" in res:
        print(json.dumps(res, indent=2))
        return
    # Extract plain text
    content_list = []
    body = res.get("body", {}).get("content", [])
    for elem in body:
        p = elem.get("paragraph", {})
        for pe in p.get("elements", []):
            t = pe.get("textRun", {}).get("content", "")
            if t:
                content_list.append(t)
    print("".join(content_list))


def docs_create(args):
    url = "https://docs.googleapis.com/v1/documents"
    payload = {"title": args.title}
    res = api_request("POST", url, data=payload, account=args.account)
    if "documentId" in res and args.text:
        doc_id = res["documentId"]
        ins_url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
        ins_payload = {
            "requests": [
                {"insertText": {"location": {"index": 1}, "text": args.text}}
            ]
        }
        api_request("POST", ins_url, data=ins_payload, account=args.account)
    print(json.dumps(res, indent=2, ensure_ascii=False))


# --- Google Drive ---
def drive_search(args):
    q = f"name contains '{args.query}' and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(q)}&pageSize={args.max}&fields=files(id,name,mimeType,webViewLink,modifiedTime)"
    res = api_request("GET", url, account=args.account)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def drive_upload(args):
    path = Path(args.file_path).expanduser().resolve()
    if not path.exists():
        print(f"Error: file {path} tidak ditemukan")
        return

    token = get_access_token(args.account)
    name = args.name or path.name

    metadata = {"name": name}
    if args.folder:
        metadata["parents"] = [args.folder]

    boundary = "-------HermesBoundaryXYZ"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/related; boundary={boundary}",
    }

    meta_part = f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(metadata)}\r\n"
    file_bytes = path.read_bytes()
    media_part = f"--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n".encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req_data = meta_part.encode("utf-8") + media_part
    req = urllib.request.Request("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart", data=req_data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(resp.read().decode())
    except Exception as e:
        print(f"Upload error: {e}")


def drive_share(args):
    url = f"https://www.googleapis.com/drive/v3/files/{args.file_id}/permissions"
    payload = {"role": args.role, "type": "anyone"}
    res = api_request("POST", url, data=payload, account=args.account)
    # Get share link
    meta_url = f"https://www.googleapis.com/drive/v3/files/{args.file_id}?fields=webViewLink,name"
    meta = api_request("GET", meta_url, account=args.account)
    print(json.dumps({"permission": res, "link": meta.get("webViewLink")}, indent=2, ensure_ascii=False))


# --- Google Photos ---
def photos_list(args):
    url = f"https://photoslibrary.googleapis.com/v1/mediaItems?pageSize={args.max}"
    res = api_request("GET", url, account=args.account)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def photos_albums(args):
    url = f"https://photoslibrary.googleapis.com/v1/albums?pageSize={args.max}"
    res = api_request("GET", url, account=args.account)
    print(json.dumps(res, indent=2, ensure_ascii=False))


# --- Google Calendar ---
def calendar_list(args):
    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults={args.max}&orderBy=startTime&singleEvents=true&timeMin={datetime.now(timezone.utc).isoformat()}"
    res = api_request("GET", url, account=args.account)
    items = []
    for item in res.get("items", []):
        items.append({
            "id": item.get("id"),
            "summary": item.get("summary"),
            "start": item.get("start", {}).get("dateTime", item.get("start", {}).get("date")),
            "end": item.get("end", {}).get("dateTime", item.get("end", {}).get("date")),
            "location": item.get("location"),
        })
    print(json.dumps(items, indent=2, ensure_ascii=False))


def calendar_create(args):
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    if args.meet:
        url += "?conferenceDataVersion=1"
    
    payload = {
        "summary": args.summary,
        "description": args.description,
        "start": {"dateTime": args.start},
        "end": {"dateTime": args.end},
    }
    if args.location:
        payload["location"] = args.location
    if args.meet:
        import uuid
        payload["conferenceData"] = {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        }
    res = api_request("POST", url, data=payload, account=args.account)
    meet_link = res.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")
    print(json.dumps({
        "status": "created",
        "id": res.get("id"),
        "htmlLink": res.get("htmlLink"),
        "meetLink": meet_link or None
    }, indent=2, ensure_ascii=False))


# --- Google Tasks ---
def tasks_list(args):
    list_id = args.list_id or "@default"
    url = f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks"
    res = api_request("GET", url, account=args.account)
    items = []
    for item in res.get("items", []):
        items.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "status": item.get("status"),
            "due": item.get("due"),
            "notes": item.get("notes"),
        })
    print(json.dumps(items, indent=2, ensure_ascii=False))


# --- Gmail ---
def gmail_search(args):
    q = urllib.parse.quote(args.query)
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={q}&maxResults={args.max}"
    res = api_request("GET", url, account=args.account)
    msgs = []
    for m in res.get("messages", []):
        mid = m["id"]
        detail = api_request("GET", f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}?format=metadata", account=args.account)
        headers = {h["name"].lower(): h["value"] for h in detail.get("payload", {}).get("headers", [])}
        msgs.append({
            "id": mid,
            "snippet": detail.get("snippet"),
            "subject": headers.get("subject", ""),
            "from": headers.get("from", ""),
            "date": headers.get("date", "")
        })
    print(json.dumps(msgs, indent=2, ensure_ascii=False))


def gmail_send(args):
    import base64
    from email.mime.text import MIMEText
    msg = MIMEText(args.body)
    msg["to"] = args.to
    msg["subject"] = args.subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    res = api_request("POST", url, data={"raw": raw}, account=args.account)
    print(json.dumps({"status": "sent", "id": res.get("id")}, indent=2, ensure_ascii=False))


# --- Google Classroom ---
def classroom_courses(args):
    url = f"https://classroom.googleapis.com/v1/courses?pageSize={args.max}&courseStates=ACTIVE"
    res = api_request("GET", url, account=args.account)
    courses = []
    for c in res.get("courses", []):
        courses.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "section": c.get("section"),
            "room": c.get("room"),
            "alternateLink": c.get("alternateLink")
        })
    print(json.dumps(courses, indent=2, ensure_ascii=False))


def classroom_coursework(args):
    url = f"https://classroom.googleapis.com/v1/courses/{args.course_id}/courseWork?pageSize={args.max}"
    res = api_request("GET", url, account=args.account)
    items = []
    for w in res.get("courseWork", []):
        items.append({
            "id": w.get("id"),
            "title": w.get("title"),
            "description": w.get("description"),
            "dueDate": w.get("dueDate"),
            "dueTime": w.get("dueTime"),
            "alternateLink": w.get("alternateLink")
        })
    print(json.dumps(items, indent=2, ensure_ascii=False))


def classroom_announcements(args):
    url = f"https://classroom.googleapis.com/v1/courses/{args.course_id}/announcements?pageSize={args.max}"
    res = api_request("GET", url, account=args.account)
    items = []
    for a in res.get("announcements", []):
        items.append({
            "id": a.get("id"),
            "text": a.get("text"),
            "updateTime": a.get("updateTime"),
            "alternateLink": a.get("alternateLink")
        })
    print(json.dumps(items, indent=2, ensure_ascii=False))


# --- Google Slides ---
def slides_create(args):
    url = "https://slides.googleapis.com/v1/presentations"
    res = api_request("POST", url, data={"title": args.title}, account=args.account)
    print(json.dumps({
        "status": "created",
        "presentationId": res.get("presentationId"),
        "title": res.get("title")
    }, indent=2, ensure_ascii=False))


def slides_get(args):
    url = f"https://slides.googleapis.com/v1/presentations/{args.presentation_id}"
    res = api_request("GET", url, account=args.account)
    print(json.dumps({
        "presentationId": res.get("presentationId"),
        "title": res.get("title"),
        "slideCount": len(res.get("slides", []))
    }, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Unified Google Workspace Tool for UNESA")
    parser.add_argument("--account", choices=["personal", "sso", "unesa"], default=None, help="Akun Google (personal vs sso)")
    sub = parser.add_subparsers(dest="service", required=True)

    # Sheets
    s_parser = sub.add_parser("sheets")
    s_sub = s_parser.add_subparsers(dest="action", required=True)
    p = s_sub.add_parser("get")
    p.add_argument("sheet_id")
    p.add_argument("--range", default="Sheet1!A1:Z100")
    p.set_defaults(func=sheets_get)

    p = s_sub.add_parser("append")
    p.add_argument("sheet_id")
    p.add_argument("--values", required=True, help="Nilai dipisah koma")
    p.add_argument("--range", default="Sheet1!A1")
    p.set_defaults(func=sheets_append)

    p = s_sub.add_parser("create")
    p.add_argument("--title", required=True)
    p.set_defaults(func=sheets_create)

    # Docs
    d_parser = sub.add_parser("docs")
    d_sub = d_parser.add_subparsers(dest="action", required=True)
    p = d_sub.add_parser("get")
    p.add_argument("doc_id")
    p.set_defaults(func=docs_get)

    p = d_sub.add_parser("create")
    p.add_argument("--title", required=True)
    p.add_argument("--text", default="")
    p.set_defaults(func=docs_create)

    # Drive
    dr_parser = sub.add_parser("drive")
    dr_sub = dr_parser.add_subparsers(dest="action", required=True)
    p = dr_sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=10)
    p.set_defaults(func=drive_search)

    p = dr_sub.add_parser("upload")
    p.add_argument("file_path")
    p.add_argument("--name", default=None)
    p.add_argument("--folder", default=None)
    p.set_defaults(func=drive_upload)

    p = dr_sub.add_parser("share")
    p.add_argument("file_id")
    p.add_argument("--role", default="reader", choices=["reader", "commenter", "writer"])
    p.set_defaults(func=drive_share)

    # Photos
    ph_parser = sub.add_parser("photos")
    ph_sub = ph_parser.add_subparsers(dest="action", required=True)
    p = ph_sub.add_parser("list")
    p.add_argument("--max", type=int, default=10)
    p.set_defaults(func=photos_list)

    p = ph_sub.add_parser("albums")
    p.add_argument("--max", type=int, default=10)
    p.set_defaults(func=photos_albums)

    # Calendar
    c_parser = sub.add_parser("calendar")
    c_sub = c_parser.add_subparsers(dest="action", required=True)
    p = c_sub.add_parser("list")
    p.add_argument("--max", type=int, default=10)
    p.set_defaults(func=calendar_list)

    p = c_sub.add_parser("create")
    p.add_argument("--summary", required=True)
    p.add_argument("--start", required=True, help="ISO 8601 (contoh: 2026-11-05T08:00:00+07:00)")
    p.add_argument("--end", required=True, help="ISO 8601")
    p.add_argument("--description", default="")
    p.add_argument("--location", default="")
    p.add_argument("--meet", action="store_true", help="Generate link Google Meet otomatis")
    p.set_defaults(func=calendar_create)

    # Tasks
    t_parser = sub.add_parser("tasks")
    t_sub = t_parser.add_subparsers(dest="action", required=True)
    p = t_sub.add_parser("list")
    p.add_argument("--list-id", default="@default")
    p.set_defaults(func=tasks_list)

    # Gmail
    gm_parser = sub.add_parser("gmail")
    gm_sub = gm_parser.add_subparsers(dest="action", required=True)
    p = gm_sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=10)
    p.set_defaults(func=gmail_search)

    p = gm_sub.add_parser("send")
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.set_defaults(func=gmail_send)

    # Classroom
    cr_parser = sub.add_parser("classroom")
    cr_sub = cr_parser.add_subparsers(dest="action", required=True)
    p = cr_sub.add_parser("courses")
    p.add_argument("--max", type=int, default=15)
    p.set_defaults(func=classroom_courses)

    p = cr_sub.add_parser("coursework")
    p.add_argument("course_id")
    p.add_argument("--max", type=int, default=15)
    p.set_defaults(func=classroom_coursework)

    p = cr_sub.add_parser("announcements")
    p.add_argument("course_id")
    p.add_argument("--max", type=int, default=15)
    p.set_defaults(func=classroom_announcements)

    # Slides
    sl_parser = sub.add_parser("slides")
    sl_sub = sl_parser.add_subparsers(dest="action", required=True)
    p = sl_sub.add_parser("create")
    p.add_argument("--title", required=True)
    p.set_defaults(func=slides_create)

    p = sl_sub.add_parser("get")
    p.add_argument("presentation_id")
    p.set_defaults(func=slides_get)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
