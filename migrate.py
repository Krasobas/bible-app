#!/usr/bin/env python3
"""
Migration script: import existing Luke course content into the Bible Study web app.

Usage:
    1. Start the app: uvicorn app.main:app
    2. Run this script: python migrate.py --api-url http://localhost:8000 --api-key YOUR_KEY

Extracts content from existing static HTML lecture files and uploads them via the API.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)


# ── Content extraction ──

def extract_content(html: str) -> str:
    """Extract the main content from a static HTML lecture file.

    Looks for content between the first <h1> and the footer.
    Returns the inner HTML without the wrapper.
    """
    # Try to find content between <h1> and footer
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not h1_match:
        # Try to find content in scripture-column
        col_match = re.search(r'<div[^>]*class="[^"]*scripture-column[^"]*"[^>]*>(.*?)</div>\s*<!--\s*/scripture-column\s*-->', html, re.DOTALL)
        if col_match:
            return col_match.group(1).strip()

    # Find everything from <h1> to the footer
    start = h1_match.start() if h1_match else 0
    footer_match = re.search(r'<div[^>]*class="[^"]*footer[^"]*"', html)
    end = footer_match.start() if footer_match else len(html)

    content = html[start:end].strip()

    # Remove the old navigation bar if present
    content = re.sub(r'<nav[^>]*class="[^"]*topbar[^"]*"[^>]*>.*?</nav>', '', content, flags=re.DOTALL)

    return content


def extract_title(html: str) -> str:
    """Extract the <h1> text."""
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    return m.group(1).strip() if m else "Untitled"


def extract_subtitle(html: str) -> str:
    """Extract the subtitle."""
    m = re.search(r'<p[^>]*class="[^"]*subtitle[^"]*"[^>]*>(.*?)</p>', html, re.DOTALL)
    return m.group(1).strip() if m else ""


# ── Lecture definitions ──

LECTURES = [
    {
        "slug": "1-2",
        "chapter_start": 1,
        "chapter_end": 2,
        "sort_order": 1,
        "file": "luke_1-2_lecture.html",
    },
    {
        "slug": "3-4",
        "chapter_start": 3,
        "chapter_end": 4,
        "sort_order": 2,
        "file": "luke_3-4_lecture.html",
    },
    {
        "slug": "5-6",
        "chapter_start": 5,
        "chapter_end": 6,
        "sort_order": 3,
        "file": "luke_5-6_lecture.html",
    },
    {
        "slug": "7-8",
        "chapter_start": 7,
        "chapter_end": 8,
        "sort_order": 4,
        "file": "luke_7-8_lecture.html",
    },
]

REF_PAGES = [
    {"slug": "chronology", "title": "Хронология", "sort_order": 1, "file": "ref_chronology.html"},
    {"slug": "genealogies", "title": "Генеалогии", "sort_order": 2, "file": "ref_genealogies.html"},
    {"slug": "geography", "title": "География", "sort_order": 3, "file": "ref_geography.html"},
    {"slug": "temple", "title": "Храм и ритуал", "sort_order": 4, "file": "ref_temple.html"},
    {"slug": "glossary", "title": "Глоссарий", "sort_order": 5, "file": "ref_glossary.html"},
    {"slug": "names", "title": "Указатель имён", "sort_order": 6, "file": "ref_names.html"},
]


def main():
    parser = argparse.ArgumentParser(description="Migrate Luke course content to the web app")
    parser.add_argument("--api-url", required=True, help="Base URL of the running app, e.g. http://localhost:8000")
    parser.add_argument("--api-key", required=True, help="API key for write access")
    parser.add_argument("--source-dir", default="/workspace/outputs", help="Directory with source HTML files")
    args = parser.parse_args()

    base = args.api_url.rstrip("/")
    headers = {"X-API-Key": args.api_key}
    source = Path(args.source_dir)

    # 1. Create the Luke course
    print("Creating course 'luke'...")
    r = requests.post(f"{base}/api/courses/", headers=headers, json={
        "slug": "luke",
        "title": "Евангелие от Луки",
        "subtitle": "Комментарий для XXI века",
        "description": "Подробный культурно-исторический комментарий к Евангелию от Луки (НРП). Разбираем текст, контекст, первоисточники.",
        "course_type": "book",
        "sort_order": 1,
    })
    if r.status_code == 409:
        print("  Course already exists, skipping.")
    elif r.status_code == 201:
        print("  Created.")
    else:
        print(f"  Error: {r.status_code} {r.text}")
        sys.exit(1)

    # 2. Upload lectures
    for lec_def in LECTURES:
        filepath = source / lec_def["file"]
        if not filepath.exists():
            print(f"  File not found: {filepath}, skipping.")
            continue

        print(f"Uploading lecture '{lec_def['slug']}'...")
        html = filepath.read_text(encoding="utf-8")
        content = extract_content(html)
        title = extract_title(html)
        subtitle = extract_subtitle(html)

        payload = {
            "slug": lec_def["slug"],
            "title": title,
            "subtitle": subtitle,
            "chapter_start": lec_def["chapter_start"],
            "chapter_end": lec_def["chapter_end"],
            "content": content,
            "sort_order": lec_def["sort_order"],
        }

        r = requests.post(f"{base}/api/courses/luke/lectures/", headers=headers, json=payload)
        if r.status_code == 409:
            # Try PUT instead
            r = requests.put(f"{base}/api/courses/luke/lectures/{lec_def['slug']}", headers=headers, json={
                "content": content,
                "title": title,
                "subtitle": subtitle,
            })
            print(f"  Updated (PUT).")
        elif r.status_code == 201:
            print(f"  Created.")
        else:
            print(f"  Error: {r.status_code} {r.text}")

    # 3. Upload reference pages
    for ref_def in REF_PAGES:
        filepath = source / ref_def["file"]
        if not filepath.exists():
            print(f"  File not found: {filepath}, skipping.")
            continue

        print(f"Uploading reference '{ref_def['slug']}'...")
        html = filepath.read_text(encoding="utf-8")
        content = extract_content(html)

        payload = {
            "slug": ref_def["slug"],
            "title": ref_def["title"],
            "content": content,
            "sort_order": ref_def["sort_order"],
        }

        r = requests.post(f"{base}/api/courses/luke/reference/", headers=headers, json=payload)
        if r.status_code == 409:
            r = requests.put(f"{base}/api/courses/luke/reference/{ref_def['slug']}", headers=headers, json={
                "content": content,
                "title": ref_def["title"],
            })
            print(f"  Updated (PUT).")
        elif r.status_code == 201:
            print(f"  Created.")
        else:
            print(f"  Error: {r.status_code} {r.text}")

    # 4. Upload images
    img_dir = source / "img"
    if img_dir.exists():
        for img_file in sorted(img_dir.iterdir()):
            if img_file.is_file() and img_file.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                print(f"Uploading image '{img_file.name}'...")
                with open(img_file, "rb") as f:
                    r = requests.post(
                        f"{base}/api/images/?course_slug=luke",
                        headers=headers,
                        files={"file": (img_file.name, f, f"image/{img_file.suffix[1:]}")},
                    )
                if r.status_code == 201:
                    print(f"  Uploaded: {r.json()['url']}")
                else:
                    print(f"  Error: {r.status_code} {r.text}")

    print("\nDone! Visit:", base)


if __name__ == "__main__":
    main()
