import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

URL = "https://www.imdb.com/chart/moviemeter/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

resp = requests.get(URL, headers=headers)
print("Status code:", resp.status_code)

soup = BeautifulSoup(resp.text, "html.parser")

ld_script = None
for s in soup.find_all("script", type="application/ld+json"):
    if "itemListElement" in s.text:
        ld_script = s
        break

if ld_script is None:
    raise RuntimeError("Could not find JSON-LD with itemListElement.")

data = json.loads(ld_script.string)
items = data.get("itemListElement", [])
print("Items in JSON:", len(items))

rows = []

for entry in items[:100]:  # Top 100 most popular
    item = entry.get("item", {})

    title = item.get("name")
    url_rel = item.get("url")
    url_full = (
        f"https://www.imdb.com{url_rel}" if url_rel and url_rel.startswith("/")
        else url_rel
    )

    rating = None
    rating_count = None
    if "aggregateRating" in item:
        rating = item["aggregateRating"].get("ratingValue")
        rating_count = item["aggregateRating"].get("ratingCount")

    summary = item.get("description")  # short plot/description if present

    rows.append({
        "Title": title,
        "Rating": rating,
        "RatingCount": rating_count,
        "URL": url_full,
        "Summary": summary,
    })

df = pd.DataFrame(rows)
print(df.head())
print("Total movies:", len(df))

df.to_csv("imdb_most_popular_top_100.csv", index=False)
print("Saved to imdb_most_popular_top_100.csv")
