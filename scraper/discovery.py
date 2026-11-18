
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from scraper.utils import create_session, is_allowed

BASE_URL = "https://darglobal.co.uk"

START_URLS = [
    f"{BASE_URL}/about",
    f"{BASE_URL}/press"
]

KEYWORDS = [
    "project", "property", "about", "press",
    "news", "development", "investment",
    "portfolio", "contact", "partner"
]

def discover_pages():
    session = create_session()
    discovered = set(START_URLS)

    for url in START_URLS:
        print(f"\n[DISCOVERING] {url}")

        if not is_allowed(url, session):
            print("[SKIPPED] Robots restriction")
            continue

        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for anchor in soup.find_all("a", href=True):
                link = urljoin(url, anchor["href"])
                parsed = urlparse(link)

                if parsed.netloc != "darglobal.co.uk":
                    continue

                if parsed.scheme != "https":
                    continue

                if any(word in link.lower() for word in KEYWORDS):
                    discovered.add(link.split("#")[0])

        except Exception as error:
            print("[ERROR]", error)

    print("\nDISCOVERED PAGES:")
    for page in sorted(discovered):
        print(page)

    return sorted(discovered)

if __name__ == "__main__":
    discover_pages()
