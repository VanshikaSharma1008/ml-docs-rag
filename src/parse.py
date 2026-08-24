import re
import requests
from bs4 import BeautifulSoup, NavigableString

URL = "https://fastapi.tiangolo.com/tutorial/first-steps/"


def parse_page(html, url):
    soup = BeautifulSoup(html, "lxml")

    article = soup.find("article", class_="md-content__inner")
    if article is None:
        raise ValueError(f"Content wrapper not found: {url}")

    # 1. Kill the ¶ anchor links that sit inside every heading
    for link in article.find_all("a", class_="headerlink"):
        link.decompose()

    # 2. Mark headings so chunking can use the structure later
    for level in range(1, 7):
        for heading in article.find_all(f"h{level}"):
            heading.string = f"{'#' * level} {heading.get_text(strip=True)}"

    # 3. Replace each code block with ONE clean text node
    for pre in article.find_all("pre"):
        code = pre.find("code")
        raw = code.get_text() if code else pre.get_text()

        # Terminal blocks embed escaped HTML for colouring — strip those tags
        if pre.find_parent("div", class_="termy"):
            raw = re.sub(r"<[^>]+>", "", raw)

        pre.replace_with(NavigableString(f"```\n{raw.strip()}\n```"))

    # 4. Now the global separator can't shred anything
    text = article.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


if __name__ == "__main__":
    response = requests.get(URL, timeout=10)
    text = parse_page(response.text, URL)

    print("Original HTML length:", len(response.text))
    print("Extracted text length:", len(text))
    print("\n--- First 1200 chars ---\n")
    print(text[:1200])