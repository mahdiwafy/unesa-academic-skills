#!/usr/bin/env python3
"""
Google Forms Academic Automation Tool (gform_tool.py)
Dual-Engine: Cloud Draft Autosave (via Chrome CDP) & Instant Prefilled URL.

100% Generic, Self-Hosted, and White-Labeled for Academic AI Agents.
"""

import sys
import os
import re
import json
import argparse
import urllib.parse
from typing import Dict, Any, List, Optional

try:
    import requests
except ImportError:
    requests = None

# Mapping Google Forms internal question type IDs to human-readable names
TYPE_MAP = {
    0: "Short Text",
    1: "Paragraph",
    2: "Multiple Choice (Radio)",
    3: "Dropdown",
    4: "Checkboxes",
    5: "Linear Scale",
    7: "Grid / Matrix",
    9: "Date",
    10: "Time",
    13: "File Upload",
}


def normalize_form_url(url_or_id: str) -> str:
    """Normalize input URL or ID into a clean viewform URL."""
    url = url_or_id.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        if "/" not in url:
            return f"https://docs.google.com/forms/d/e/{url}/viewform"
        url = f"https://{url}"

    # Unshorten redirect if using shortlink (forms.gle, bit.ly, unesa.me, s.id)
    if any(domain in url for domain in ["forms.gle", "bit.ly", "unesa.me", "s.id", "tinyurl.com"]):
        if requests is not None:
            try:
                resp = requests.head(url, allow_redirects=True, timeout=10)
                url = resp.url
            except Exception:
                pass

    # Normalize edit/viewscore to viewform
    url = re.sub(r"/(edit|viewscore|formResponse).*$", "/viewform", url)
    if "docs.google.com/forms" in url and not url.endswith("/viewform"):
        url = url.rstrip("/") + "/viewform"
    return url


def parse_form_schema(url_or_id: str) -> Dict[str, Any]:
    """
    Fast metadata & question schema extraction via HTTP GET.
    Parses Google Forms' FB_PUBLIC_LOAD_DATA_ without launching a browser.
    """
    if requests is None:
        raise ImportError("Package 'requests' diperlukan. Jalankan: pip install requests")

    form_url = normalize_form_url(url_or_id)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(form_url, headers=headers, timeout=15)
    resp.raise_for_status()
    html = resp.text

    match = re.search(r"var FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);\s*</script>", html, re.DOTALL)
    if not match:
        match = re.search(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);", html, re.DOTALL)

    if not match:
        raise ValueError("FB_PUBLIC_LOAD_DATA_ tidak ditemukan. Formulir mungkin privat atau memerlukan login kampus.")

    data = json.loads(match.group(1))
    title = data[1][8] if len(data) > 1 and len(data[1]) > 8 and data[1][8] else (data[3] if len(data) > 3 else "Google Form")
    description = data[1][0] if len(data) > 1 and len(data[1]) > 0 and data[1][0] else ""

    fields = []
    raw_fields = data[1][1] if len(data) > 1 and len(data[1]) > 1 and data[1][1] else []

    for item in raw_fields:
        if not item or len(item) < 5 or not item[4]:
            continue
        field_id = item[0]
        field_title = item[1] or "Tanpa Judul"
        field_type_id = item[3]
        field_required = bool(item[4][0][2]) if len(item[4][0]) > 2 else False
        entry_id = item[4][0][0]

        options = []
        if len(item[4][0]) > 1 and item[4][0][1]:
            options = [opt[0] for opt in item[4][0][1] if opt and len(opt) > 0 and opt[0] is not None]

        fields.append({
            "id": field_id,
            "title": field_title,
            "entry_id": f"entry.{entry_id}" if entry_id else None,
            "type_id": field_type_id,
            "type_name": TYPE_MAP.get(field_type_id, f"Unknown ({field_type_id})"),
            "required": field_required,
            "options": options,
        })

    return {
        "form_url": form_url,
        "title": title,
        "description": description,
        "total_fields": len(fields),
        "fields": fields,
    }


def generate_prefill_url(form_url: str, mapping: Dict[str, Any], authuser: Optional[str] = None) -> str:
    """
    Constructs an instant prefilled URL (usp=pp_url).
    Injects authuser parameter for automatic Google SSO routing if provided.
    """
    clean_url = normalize_form_url(form_url)
    params = {"usp": "pp_url"}
    if authuser:
        params["authuser"] = authuser

    for k, v in mapping.items():
        if v is None:
            continue
        key = k if k.startswith("entry.") else f"entry.{k}"
        params[key] = str(v)

    return f"{clean_url}?{urllib.parse.urlencode(params)}"


async def create_cloud_draft(
    form_url: str,
    answers: Dict[str, Any],
    authuser: Optional[str] = None,
    cdp_url: str = "http://localhost:9222",
    files: Optional[Dict[str, str]] = None,
    screenshot_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Mode Utama: Simpan draf ke server cloud Google via Chrome CDP (:9222).
    Mengisi seluruh input secara alami, menangani upload berkas Google Picker,
    dan menunggu indikator 'Draf disimpan' / 'Draft saved'.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError("Playwright belum terpasang. Jalankan: pip install playwright")

    clean_url = normalize_form_url(form_url)
    target_url = clean_url
    if authuser:
        delimiter = "&" if "?" in target_url else "?"
        target_url = f"{target_url}{delimiter}authuser={urllib.parse.quote(authuser)}"

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            raise ConnectionError(
                f"Gagal terhubung ke Chrome CDP di {cdp_url}. Pastikan Chrome dijalankan dengan "
                f"'--remote-debugging-port=9222'. Error: {e}"
            )

        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
        except Exception:
            # Fallback to domcontentloaded if networkidle times out
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)

        import asyncio
        await asyncio.sleep(1.0)

        # 1. Handle email recording consent checkbox if present and unchecked
        try:
            consent_cb = await page.query_selector('div[role="checkbox"]')
            if consent_cb:
                checked = await consent_cb.get_attribute("aria-checked")
                if checked != "true":
                    await consent_cb.click()
                    await asyncio.sleep(0.3)
        except Exception:
            pass

        # 2. Fill text and textarea inputs
        # Match by question title or fill sequentially
        text_inputs = await page.query_selector_all('input[type="text"], input[type="email"], textarea')
        filled_count = 0

        # Map entries to values
        for inp in text_inputs:
            aria_label = await inp.get_attribute("aria-label") or ""
            placeholder = await inp.get_attribute("placeholder") or ""
            
            # Find matching answer from dictionary
            val_to_fill = None
            for key, val in answers.items():
                if val is None:
                    continue
                # If key matches entry ID or key substring in aria-label
                clean_key = key.replace("entry.", "").lower()
                if clean_key in aria_label.lower() or key.lower() in aria_label.lower():
                    val_to_fill = str(val)
                    break

            if val_to_fill:
                await inp.click()
                await inp.fill(val_to_fill)
                filled_count += 1
                await asyncio.sleep(0.2)

        # If keyed mapping didn't match aria-labels, try sequential filling for simple dicts
        if filled_count == 0 and text_inputs:
            values_list = [str(v) for v in answers.values() if v is not None]
            for inp, val in zip(text_inputs, values_list):
                try:
                    await inp.click()
                    await inp.fill(val)
                    filled_count += 1
                    await asyncio.sleep(0.2)
                except Exception:
                    pass

        # 3. Handle Radio Buttons & Dropdowns
        for val in answers.values():
            if val is None:
                continue
            str_val = str(val).strip()
            # Try radio button
            try:
                radio = await page.query_selector(f'div[role="radio"][data-value="{str_val}"], div[role="radio"]:has-text("{str_val}")')
                if radio:
                    await radio.click()
                    await asyncio.sleep(0.3)
            except Exception:
                pass

        # 4. Handle File Upload via Google Picker if files provided
        if files:
            for field_hint, file_path in files.items():
                if not os.path.exists(file_path):
                    continue
                filename = os.path.basename(file_path)
                body_text = await page.inner_text("body")
                
                # Draft restore guard: skip if file already attached from existing draft
                if filename in body_text:
                    continue

                add_btn = page.locator('div[role="button"]:has-text("Tambahkan file"), div[role="button"]:has-text("Add file")').first
                if await add_btn.count() > 0 and await add_btn.is_visible():
                    await add_btn.click()
                    await asyncio.sleep(2.0)

                    # Look for Google Picker frame
                    picker_frame = None
                    for frame in page.frames:
                        if "picker" in frame.url or "upload" in frame.url:
                            picker_frame = frame
                            break

                    if picker_frame:
                        file_input = await picker_frame.wait_for_selector('input[type="file"]', state="attached", timeout=10000)
                        if file_input:
                            await file_input.set_input_files(file_path)
                            # Wait for upload to complete
                            for _ in range(20):
                                await asyncio.sleep(1.0)
                                if filename in await page.inner_text("body"):
                                    break
                    # Dismiss modal if still open
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.5)

        # 5. Wait for Google Forms cloud autosave indicator
        autosaved = False
        status_text = ""
        for _ in range(12):
            await asyncio.sleep(1.0)
            body = await page.inner_text("body")
            if "Draf disimpan" in body or "Draft saved" in body:
                autosaved = True
                status_text = "Draf disimpan (Cloud Draft Saved)"
                break
            elif "Menyimpan..." in body or "Saving..." in body:
                status_text = "Sedang menyimpan..."

        # 6. Capture screenshot verification if requested
        screenshot_done = None
        if screenshot_path:
            os.makedirs(os.path.dirname(os.path.abspath(screenshot_path)), exist_ok=True)
            await page.screenshot(path=screenshot_path, full_page=True)
            screenshot_done = os.path.abspath(screenshot_path)

        form_title = await page.title()
        await page.close()

        return {
            "success": True,
            "mode": "cloud_draft",
            "form_url": clean_url,
            "form_title": form_title,
            "autosaved": autosaved,
            "status_indicator": status_text or ("Selesai diisi" if filled_count > 0 else "Belum terdeteksi status"),
            "inputs_filled": filled_count,
            "screenshot": screenshot_done,
        }


def submit_form_headless(form_url: str, mapping: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submits answers directly via HTTP POST to /formResponse.
    Verifies submission confirmation and extracts embedded WhatsApp group links.
    """
    if requests is None:
        raise ImportError("Package 'requests' diperlukan. Jalankan: pip install requests")

    clean_url = normalize_form_url(form_url)
    submit_url = re.sub(r"/viewform.*$", "/formResponse", clean_url)
    if not submit_url.endswith("/formResponse"):
        submit_url = submit_url.rstrip("/") + "/formResponse"

    payload = {}
    for k, v in mapping.items():
        if v is None:
            continue
        key = k if k.startswith("entry.") else f"entry.{k}"
        payload[key] = str(v)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    resp = requests.post(submit_url, data=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    html = resp.text

    # Verify confirmation text
    success_patterns = [
        r"telah direkam",
        r"your response has been recorded",
        r"terima kasih",
        r"jawaban anda telah dikirim",
    ]
    confirmed = any(re.search(pat, html, re.IGNORECASE) for pat in success_patterns)

    # Extract WhatsApp invite links
    wa_links = list(set(re.findall(r"https://chat\.whatsapp\.com/[A-Za-z0-9]+", html)))

    return {
        "success": confirmed,
        "status_code": resp.status_code,
        "confirmed": confirmed,
        "submit_url": submit_url,
        "whatsapp_group_links": wa_links,
    }


def load_profile(profile_path: Optional[str]) -> Dict[str, Any]:
    """Loads a student/user profile JSON safely."""
    if not profile_path or not os.path.exists(profile_path):
        return {}
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Google Forms Academic Automation Tool (Cloud Draft & Instant Prefill)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspeksi pertanyaan dan schema form tanpa browser")
    inspect_parser.add_argument("url", help="URL Google Form atau Shortlink (forms.gle/...)")
    inspect_parser.add_argument("--json", action="store_true", help="Output format JSON mentah")

    # 2. prefill
    prefill_parser = subparsers.add_parser("prefill", help="Buat URL draf instan (usp=pp_url)")
    prefill_parser.add_argument("url", help="URL Google Form")
    prefill_parser.add_argument("--data", help="JSON string data jawaban (contoh: '{\"entry.123\": \"Ahmad\"}')")
    prefill_parser.add_argument("--profile", help="Path berkas profile.json")
    prefill_parser.add_argument("--authuser", help="Email SSO UNESA / Akun Google (contoh: 'mhs@unesa.ac.id')")

    # 3. cloud-draft
    draft_parser = subparsers.add_parser("cloud-draft", help="Isi dan simpan draf ke cloud Google via Chrome CDP (:9222)")
    draft_parser.add_argument("url", help="URL Google Form")
    draft_parser.add_argument("--data", help="JSON string data jawaban")
    draft_parser.add_argument("--profile", help="Path berkas profile.json")
    draft_parser.add_argument("--authuser", help="Email SSO Google untuk navigasi profil akun")
    draft_parser.add_argument("--cdp", default="http://localhost:9222", help="URL Chrome CDP (default: http://localhost:9222)")
    draft_parser.add_argument("--file", action="append", help="Upload berkas dengan format: field_name=path/file.pdf")
    draft_parser.add_argument("--screenshot", help="Simpan screenshot verifikasi draf (contoh: draft.png)")

    # 4. submit
    submit_parser = subparsers.add_parser("submit", help="Submit formulir secara headless (POST /formResponse)")
    submit_parser.add_argument("url", help="URL Google Form")
    submit_parser.add_argument("--data", required=True, help="JSON string data jawaban")

    args = parser.parse_args()

    if args.command == "inspect":
        schema = parse_form_schema(args.url)
        if args.json:
            print(json.dumps(schema, indent=2, ensure_ascii=False))
        else:
            print(f"📋 Judul Form: {schema['title']}")
            if schema["description"]:
                print(f"📝 Deskripsi : {schema['description'][:100]}...")
            print(f"🔢 Total Pertanyaan: {schema['total_fields']}")
            print("-" * 65)
            for idx, f in enumerate(schema["fields"], 1):
                req_badge = "[WAJIB]" if f["required"] else "[OPSIONAL]"
                print(f"{idx}. {f['title']} {req_badge}")
                print(f"   Entry ID: {f['entry_id']} | Tipe: {f['type_name']}")
                if f["options"]:
                    print(f"   Opsi    : {', '.join(f['options'][:6])}")
            print("-" * 65)

    elif args.command == "prefill":
        answers = {}
        if args.profile:
            answers.update(load_profile(args.profile).get("answers", {}))
        if args.data:
            answers.update(json.loads(args.data))

        url = generate_prefill_url(args.url, answers, authuser=args.authuser)
        print(url)

    elif args.command == "cloud-draft":
        import asyncio
        answers = {}
        if args.profile:
            profile_data = load_profile(args.profile)
            answers.update(profile_data.get("answers", {}))
            if not args.authuser and "authuser" in profile_data:
                args.authuser = profile_data["authuser"]

        if args.data:
            answers.update(json.loads(args.data))

        files_map = {}
        if args.file:
            for item in args.file:
                if "=" in item:
                    k, v = item.split("=", 1)
                    files_map[k] = v

        result = asyncio.run(
            create_cloud_draft(
                args.url,
                answers,
                authuser=args.authuser,
                cdp_url=args.cdp,
                files=files_map,
                screenshot_path=args.screenshot,
            )
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "submit":
        answers = json.loads(args.data)
        result = submit_form_headless(args.url, answers)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
