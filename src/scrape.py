import json
import time
from pathlib import Path

import requests

from parse import parse_page
from sitemap import get_urls

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def slugify(url):
    path = url.replace("https://fastapi.tiangolo.com/", "").strip("/")
    return path.replace("/", "_") or "index"


def scrape(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return parse_page(response.text, url)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    _, urls = get_urls()
    print(f"Scraping {len(urls)} pages...\n")

    ok, failed = 0, 0

    for i, url in enumerate(urls, 1):
        try:
            text = scrape(url)
        except Exception as e:
            print(f"[{i}/{len(urls)}] FAILED {url}: {e}")
            failed += 1
            continue

        record = {
            "url": url,
            "tool": "fastapi",
            "source_type": "docs",
            "text": text,
        }

        out = RAW_DIR / f"fastapi_{slugify(url)}.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"[{i}/{len(urls)}] {out.name}  ({len(text)} chars)")
        ok += 1
        time.sleep(1)

    print(f"\nDone. {ok} saved, {failed} failed.")


if __name__ == "__main__":
    main()