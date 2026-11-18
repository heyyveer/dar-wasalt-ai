
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import response
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
import trafilatura
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "DarWasaltResearchBot/1.0 (educational project)"

def create_session():
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def is_allowed(url, session):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        response = session.get(robots_url, timeout=15)
        if response.status_code == 404:
            return True

        response.raise_for_status()
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(response.text.splitlines())
        return parser.can_fetch(USER_AGENT, url)

    except requests.RequestException:
        print(f"[ROBOTS CHECK FAILED] {robots_url}")
        return False

def scrape_page(url, source, session):
    if not is_allowed(url, session):
        print(f"[SKIPPED] Not permitted: {url}")
        return None

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        print(f"[HTTP] {response.status_code} | {response.url}")
        print(f"[HTML SIZE] {len(response.text)} characters")
        html = response.text
        text = trafilatura.extract(
            html,
            include_links=True,
            include_tables=True,
            favor_precision=True
        )

        if not text or len(text.strip()) < 100:
            print(f"[SKIPPED] Insufficient content: {url}")
            return None

        metadata = trafilatura.extract_metadata(html)

        return {
            "source": source,
            "url": url,
            "title": metadata.title if metadata else None,
            "text": text.strip(),
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }

    except requests.RequestException as error:
        print(f"[ERROR] {url}: {error}")
        return None

def save_records(records, filename):
    output_path = DATA_DIR / filename

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    print(f"[SAVED] {len(records)} records -> {output_path}")
