"""
convert_shopify_export.py
=========================
Converts a Shopify product CSV into the expanded catalog.json format
with all 18 feature fields. Empty fields are included as placeholders
for you to fill in manually.

Usage: uv run convert_shopify_export.py
"""

import csv
import json
import re
import sys
import os

def convert(input_file="products.csv", output_file="catalog.json"):
    if not os.path.exists(input_file):
        print(f"ERROR: '{input_file}' not found.")
        print("Export from Shopify Admin → Products → Export, save as products.csv")
        sys.exit(1)

    books = []
    seen = set()

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            handle = row.get("Handle", "")
            if handle in seen or not handle:
                continue
            seen.add(handle)

            title = row.get("Title", "").strip()
            if not title:
                continue

            price = row.get("Variant Price", "0.00")
            try:
                price = f"{float(price):.2f}"
            except (ValueError, TypeError):
                price = "0.00"

            desc = row.get("Body (HTML)", "")
            desc = re.sub(r'<[^>]+>', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc).strip()[:500]

            tags_raw = row.get("Tags", "")
            tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]

            language = "English"
            for tag in tags:
                for lang in ["urdu", "arabic", "french", "spanish", "german", "indonesian", "bengali", "turkish", "persian"]:
                    if lang in tag:
                        language = lang.title()

            category = row.get("Product Type", "") or row.get("Type", "General") or "General"
            vendor = row.get("Vendor", "")
            author = "" if vendor.lower() in ["ami bookstore", "amibookstore", ""] else vendor

            book = {
                "handle": handle,
                "title": title,
                "author": author,
                "author_citation": author,
                "price": price,
                "year_published": "",
                "publisher": "Islam International Publications",
                "city_published": "Tilford, UK",
                "isbn": "",
                "description": desc,
                "summary": "",
                "key_quotes": [],
                "table_of_contents": [],
                "category": category,
                "language": language,
                "translations": {},
                "tags": tags,
                "trigger_queries": [],
                "rebuttals": [],
                "comparative_topics": [],
                "theological_debates": [],
                "theological_summary": "",
                "rebuttal_summary": "",
                "true_islam_points": [],
                "true_islam_response": "",
                "media_references": [],
                "gift_suitable": False,
                "age_range": "",
                "audience": "adult",
                "occasions": [],
                "url": f"https://amibookstore.us/products/{handle}",
                "amazon_url": ""
            }
            books.append(book)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(books)} products → {output_file}")
    print(f"\nNEXT STEPS:")
    print(f"  1. Open {output_file} in a text editor")
    print(f"  2. Fill in empty fields: summary, key_quotes, trigger_queries, etc.")
    print(f"  3. See DATA_ACQUISITION_GUIDE.md for what goes in each field")

if __name__ == "__main__":
    convert()
