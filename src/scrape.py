import json
import time
from pathlib import Path

import requests

from parse import parse_page

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

URLS = [
    "https://fastapi.tiangolo.com/tutorial/first-steps/",
    "https://fastapi.tiangolo.com/tutorial/path-params/",
    "https://fastapi.tiangolo.com/tutorial/query-params/",
]


def slugify(url):
    return url.strip("/").split("/")[-1] or "index"


def scrape(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return parse_page(response.text, url)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for url in URLS:
        try:
            text = scrape(url)
        except Exception as e:
            print(f"FAILED {url}: {e}")
            continue

        record = {
            "url": url,
            "tool": "fastapi",
            "source_type": "docs",
            "text": text,
        }

        out = RAW_DIR / f"fastapi_{slugify(url)}.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"saved {out.name}  ({len(text)} chars)")
        time.sleep(1)


if __name__ == "__main__":
    main()