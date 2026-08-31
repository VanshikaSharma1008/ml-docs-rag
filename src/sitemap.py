import requests
from bs4 import BeautifulSoup

SITEMAP = "https://fastapi.tiangolo.com/sitemap.xml"

# Sections worth indexing
KEEP_PREFIXES = (
    "https://fastapi.tiangolo.com/tutorial/",
    "https://fastapi.tiangolo.com/advanced/",
    "https://fastapi.tiangolo.com/how-to/",
    "https://fastapi.tiangolo.com/deployment/",
)


def get_urls():
    response = requests.get(SITEMAP, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")
    all_urls = [loc.get_text(strip=True) for loc in soup.find_all("loc")]

    kept = [u for u in all_urls if u.startswith(KEEP_PREFIXES)]
    return all_urls, kept


if __name__ == "__main__":
    all_urls, kept = get_urls()
    print(f"Total in sitemap: {len(all_urls)}")
    print(f"Kept after filter: {len(kept)}")
    print("\nFirst 10 kept:")
    for u in kept[:10]:
        print(" ", u)