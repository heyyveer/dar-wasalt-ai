
import time
from scraper.utils import create_session, scrape_page, save_records

URLS = [
    "https://darglobal.co.uk/",
    "https://darglobal.co.uk/about",
    "https://darglobal.co.uk/projects/properties-in-uk/apartments",
    "https://darglobal.co.uk/press"
]

def diagnose():
    session = create_session()

    urls = [
        "https://darglobal.co.uk/",
        "https://darglobal.co.uk/about",
        "https://darglobal.co.uk/projects/properties-in-uk/apartments"
    ]

    for url in urls:
        print("\nURL:", url)

        try:
            response = session.get(url, timeout=30)

            print("Status:", response.status_code)
            print("Final URL:", response.url)
            print("Content-Type:", response.headers.get("Content-Type"))
            print("HTML Length:", len(response.text))
            print("Response Body:")
            print(repr(response.text[:500]))

        except Exception as error:
            print("Error:", error)

if __name__ == "__main__":
    diagnose()


def run():
    session = create_session()
    records = []

    for url in URLS:
        print(f"\n[SCRAPING] {url}")

        record = scrape_page(
            url=url,
            source="DarGlobal",
            session=session
        )

        if record:
            records.append(record)
            print(f"[SUCCESS] {record['title']}")
            print(f"[CONTENT] {len(record['text'])} characters")
        else:
            print("[FAILED] No content extracted")

        time.sleep(2)

    save_records(records, "darglobal.json")
    print(f"\nTotal extracted: {len(records)}")

    return records

if __name__ == "__main__":
    run()
