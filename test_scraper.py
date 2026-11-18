
import json
from pathlib import Path

for filename in ["darglobal.json", "wasalt.json"]:
    path = Path("data/raw") / filename

    if not path.exists():
        print(f"{filename}: File not found")
        continue

    with path.open(encoding="utf-8") as file:
        records = json.load(file)

    print(f"\n{filename}")
    print("Total records:", len(records))

    for record in records:
        print("Title:", record["title"])
        print("Source:", record["source"])
        print("Content length:", len(record["text"]))
        print("URL:", record["url"])
