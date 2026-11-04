#!/usr/bin/env python3
"""Vinesa UNESA (Moodle LMS) REST API Tool (vinesa_tool.py)
Automates course tracking, assignment deadlines, lecture files,
and kuis monitoring directly from UNESA's Moodle LMS (Vinesa).

Config file: ~/.hermes/credentials/vinesa.json
{
  "token": "YOUR_MOODLE_WS_TOKEN",
  "base_url": "https://vinesa.unesa.ac.id"
}

Usage:
  python3 vinesa_tool.py status
  python3 vinesa_tool.py courses
  python3 vinesa_tool.py assignments
  python3 vinesa_tool.py contents <course_id>
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone

CRED_FILE = os.path.expanduser("~/.hermes/credentials/vinesa.json")
DEFAULT_URL = "https://vinesa.unesa.ac.id"


def load_config():
    if not os.path.exists(CRED_FILE):
        return None
    try:
        with open(CRED_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def call_moodle(function_name, params=None, config=None):
    cfg = config or load_config()
    if not cfg or not cfg.get("token"):
        return {
            "error": True,
            "message": "Token Vinesa belum dikonfigurasi. Simpan token di ~/.hermes/credentials/vinesa.json",
            "guide": "Buka Vinesa -> Profil -> Security Keys / Mobile Web Service untuk membuat token."
        }

    token = cfg["token"]
    base = cfg.get("base_url", DEFAULT_URL).rstrip("/")
    endpoint = f"{base}/webservice/rest/server.php"

    query_params = {
        "wstoken": token,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
    }
    if params:
        query_params.update(params)

    data = urllib.parse.urlencode(query_params).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers={"User-Agent": "UNESA-Academic-Hermes/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_text = resp.read().decode("utf-8")
            return json.loads(res_text)
    except Exception as e:
        return {"error": True, "message": str(e)}


def get_status():
    res = call_moodle("core_webservice_get_site_info")
    if "error" in res or res.get("exception"):
        return res
    return {
        "status": "connected",
        "username": res.get("username"),
        "fullname": res.get("fullname"),
        "sitename": res.get("sitename"),
        "user_id": res.get("userid"),
        "moodle_version": res.get("release"),
    }


def get_courses():
    info = call_moodle("core_webservice_get_site_info")
    if "error" in info or info.get("exception"):
        return info
    userid = info.get("userid")
    courses = call_moodle("core_enrol_get_users_courses", {"userid": userid})
    if isinstance(courses, list):
        out = []
        for c in courses:
            out.append({
                "id": c.get("id"),
                "shortname": c.get("shortname"),
                "fullname": c.get("fullname"),
                "startdate": datetime.fromtimestamp(c.get("startdate", 0), tz=timezone.utc).strftime("%Y-%m-%d"),
            })
        return out
    return courses


def get_assignments():
    res = call_moodle("mod_assign_get_assignments")
    if "courses" not in res:
        return res
    
    deadlines = []
    now = datetime.now(timezone.utc).timestamp()
    for c in res.get("courses", []):
        cname = c.get("fullname", "")
        for a in c.get("assignments", []):
            due = a.get("duedate", 0)
            deadlines.append({
                "id": a.get("id"),
                "course": cname,
                "name": a.get("name"),
                "duedate_unix": due,
                "duedate": datetime.fromtimestamp(due, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if due else "No Deadline",
                "is_expired": due < now if due else False,
            })
    deadlines.sort(key=lambda x: x["duedate_unix"])
    return deadlines


def get_contents(course_id):
    res = call_moodle("core_course_get_contents", {"courseid": course_id})
    if not isinstance(res, list):
        return res
    sections = []
    for s in res:
        modules = []
        for m in s.get("modules", []):
            contents = []
            for f in m.get("contents", []):
                contents.append({
                    "filename": f.get("filename"),
                    "filesize": f.get("filesize"),
                    "fileurl": f.get("fileurl"),
                })
            modules.append({
                "id": m.get("id"),
                "name": m.get("name"),
                "modname": m.get("modname"),
                "files": contents,
            })
        sections.append({
            "name": s.get("name"),
            "modules": modules,
        })
    return sections


def main():
    parser = argparse.ArgumentParser(description="Vinesa UNESA Moodle LMS Integration")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Cek status koneksi token Vinesa")
    sub.add_parser("courses", help="Daftar mata kuliah yang diambil di Vinesa")
    sub.add_parser("assignments", help="Daftar tugas & deadline aktif di Vinesa")

    cp = sub.add_parser("contents", help="Daftar materi kuliah per pertemuan")
    cp.add_argument("course_id", type=int, help="ID mata kuliah di Vinesa")

    args = parser.parse_args()

    if args.command == "status":
        print(json.dumps(get_status(), indent=2, ensure_ascii=False))
    elif args.command == "courses":
        print(json.dumps(get_courses(), indent=2, ensure_ascii=False))
    elif args.command == "assignments":
        print(json.dumps(get_assignments(), indent=2, ensure_ascii=False))
    elif args.command == "contents":
        print(json.dumps(get_contents(args.course_id), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
