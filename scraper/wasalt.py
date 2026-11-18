
import time
from scraper.utils import create_session, scrape_page, save_records

URLS = [
    "https://wasalt.sa/en",
    "https://wasalt.sa/en/corporate",
    "https://wasalt.sa/en/international",
    "https://wasalt.sa/en/properties-for-sale-in-saudi-arabia"
]

def run():
    session = create_session()
    records = []

    for url in URLS:
        print(f"[SCRAPING] {url}")

        record = scrape_page(
            url=url,
            source="Wasalt",
            session=session
        )

        if record:
            records.append(record)
            print(f"[SUCCESS] {record['title']}")

        time.sleep(2)

    save_records(records, "wasalt.json")
    return records

if __name__ == "__main__":
    run()
