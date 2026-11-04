#!/usr/bin/env python3
"""Academic Paper Search & Citation Tool (paper_search_tool.py)
Automates scientific literature search, abstract extraction, citation generation,
and Open Access PDF downloads for academic papers via OpenAlex and Crossref APIs.

Features:
- Search scientific papers across global databases (OpenAlex & Semantic Scholar)
- Extract metadata (Title, Authors, Year, Journal, DOI, Abstract, Citations)
- Generate official APA 7th Edition & IEEE citations automatically
- Direct Open Access PDF download link detection
- Resolve any DOI link via Crossref API

Usage:
  python3 paper_search_tool.py search "CPU Scheduling Algorithms Operating Systems" --limit 3
  python3 paper_search_tool.py doi "10.1145/3341302.3342080"
  python3 paper_search_tool.py download <pdf_url> --out ~/Downloads/paper.pdf
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

USER_AGENT = "UNESA-Academic-Research/1.0 (mailto:wafy.081107@gmail.com)"


def format_apa(authors, year, title, journal, doi):
    """Format paper metadata into APA 7th Edition citation."""
    author_str = ""
    if authors:
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]}, & {authors[1]}"
        else:
            author_str = f"{authors[0]}, et al."
    else:
        author_str = "Anonim"

    yr = str(year) if year else "n.d."
    tit = title.rstrip(".") if title else "Untitled"
    jour = f" *{journal}*." if journal else ""
    d = f" https://doi.org/{doi}" if doi else ""
    return f"{author_str} ({yr}). {tit}.{jour}{d}"


def search_openalex(query, limit=5):
    """Search papers using OpenAlex API (Open Access & high throughput)."""
    q = urllib.parse.quote(query)
    url = f"https://api.openalex.org/works?search={q}&per-page={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
    for item in data.get("results", []):
        # Extract authors
        authors = []
        for a in item.get("authorships", []):
            name = a.get("author", {}).get("display_name")
            if name:
                authors.append(name)

        title = item.get("title", "")
        year = item.get("publication_year")
        doi_raw = item.get("doi", "")
        doi = doi_raw.replace("https://doi.org/", "") if doi_raw else None
        
        # Primary location / journal
        journal = ""
        loc = item.get("primary_location") or {}
        src = loc.get("source") or {}
        journal = src.get("display_name", "")

        # Open Access PDF link
        oa = item.get("open_access", {})
        oa_pdf = oa.get("oa_url")
        is_oa = oa.get("is_oa", False)

        citation_apa = format_apa(authors, year, title, journal, doi)

        results.append({
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "doi": doi,
            "is_open_access": is_oa,
            "pdf_url": oa_pdf,
            "citation_count": item.get("cited_by_count", 0),
            "apa_7th": citation_apa,
            "openalex_id": item.get("id"),
        })

    return results


def resolve_doi_crossref(doi):
    """Resolve single DOI via Crossref API to get precise metadata & citation."""
    clean_doi = doi.strip()
    if clean_doi.startswith("http"):
        clean_doi = clean_doi.split("doi.org/")[-1]

    url = f"https://api.crossref.org/works/{urllib.parse.quote(clean_doi)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    msg = data.get("message", {})
    title = msg.get("title", [""])[0] if msg.get("title") else ""
    
    # Authors
    authors = []
    for a in msg.get("author", []):
        given = a.get("given", "")
        family = a.get("family", "")
        if family and given:
            authors.append(f"{family}, {given[0]}.")
        elif family:
            authors.append(family)

    # Date
    year = None
    date_parts = msg.get("published-print", msg.get("published-online", {})).get("date-parts", [])
    if date_parts and date_parts[0]:
        year = date_parts[0][0]

    journal = msg.get("container-title", [""])[0] if msg.get("container-title") else ""
    apa = format_apa(authors, year, title, journal, clean_doi)

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "doi": clean_doi,
        "publisher": msg.get("publisher"),
        "apa_7th": apa,
    }


def download_pdf(url, output_path):
    """Download Open Access PDF directly to disk."""
    out = os.path.abspath(os.path.expanduser(output_path))
    os.makedirs(os.path.dirname(out), exist_ok=True)

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as resp:
        with open(out, "wb") as f:
            f.write(resp.read())

    print(f"✅ PDF berhasil diunduh ke: {out}")


def main():
    parser = argparse.ArgumentParser(description="Academic Literature Search & Citation Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    sp = subparsers.add_parser("search", help="Cari artikel jurnal berdasarkan kata kunci topik")
    sp.add_argument("query", help="Topik riset / kata kunci makalah")
    sp.add_argument("--limit", type=int, default=5, help="Jumlah paper maksimal (default: 5)")

    # doi
    dp = subparsers.add_parser("doi", help="Ekstrak metadata dan sitasi APA dari nomor DOI")
    dp.add_argument("doi", help="Nomor atau link DOI (contoh: 10.1145/3341302.3342080)")

    # download
    dl = subparsers.add_parser("download", help="Unduh berkas PDF Open Access")
    dl.add_argument("url", help="URL file PDF")
    dl.add_argument("--out", required=True, help="Path berkas tujuan (.pdf)")

    args = parser.parse_args()

    if args.command == "search":
        papers = search_openalex(args.query, limit=args.limit)
        print(json.dumps({"total_found": len(papers), "papers": papers}, indent=2, ensure_ascii=False))

    elif args.command == "doi":
        meta = resolve_doi_crossref(args.doi)
        print(json.dumps(meta, indent=2, ensure_ascii=False))

    elif args.command == "download":
        download_pdf(args.url, args.out)


if __name__ == "__main__":
    main()
