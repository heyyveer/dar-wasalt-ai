
import requests
import trafilatura

urls = [
    "https://darglobal.co.uk/?page_id=3",
    "https://darglobal.co.uk/about",
    "https://darglobal.co.uk/press"
]

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
})

for url in urls:
    print("\nURL:", url)

    try:
        response = session.get(url, timeout=30)

        print("Status:", response.status_code)
        print("Final URL:", response.url)
        print("HTML Size:", len(response.content))
        print("Response:", repr(response.text[:200]))

        content = trafilatura.extract(response.text)

        if content:
            print("Extracted:", len(content), "characters")
            print(content[:500])
        else:
            print("No readable content")

    except requests.RequestException as error:
        print("Error:", error)
