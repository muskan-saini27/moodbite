import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import re
import time

# ------------------------------------------------------------
# FAST RESUMABLE INDIAN RECIPE IMAGE ENRICHMENT
# ------------------------------------------------------------

INPUT = Path("moodbite_master_quality_fixed_v4_5615.csv")
OUTPUT = Path("moodbite_master_image_enriched_v1_5615.csv")
CACHE = Path("image_cache.json")

WORKERS = 12
BATCH_SIZE = 100
TIMEOUT = 12

if OUTPUT.exists():
    df = pd.read_csv(OUTPUT)
    print(f"Resuming from existing output: {OUTPUT}")
else:
    df = pd.read_csv(INPUT)
    print(f"Starting from input: {INPUT}")

# Load existing cache from the previous slow run.
if CACHE.exists():
    try:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
else:
    cache = {}

# Normalize NaN image values.
df["image_url"] = df["image_url"].fillna("").astype(str)
df.loc[df["image_url"].isin(["nan", "None"]), "image_url"] = ""

# Only recipes still missing images.
target_indices = [
    int(i) for i, row in df.iterrows()
    if not row["image_url"].strip()
]

print(f"Recipes still missing images: {len(target_indices)}")
print(f"Existing cache entries: {len(cache)}")
print(f"Concurrent workers: {WORKERS}")
print()

def clean_url(url):
    if not url:
        return ""
    url = str(url).strip()
    if url.startswith("//"):
        url = "https:" + url
    return url

def extract_image(html):
    soup = BeautifulSoup(html, "html.parser")

    # OpenGraph
    for attrs in (
        {"property": "og:image"},
        {"name": "og:image"},
        {"property": "twitter:image"},
        {"name": "twitter:image"},
    ):
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            return clean_url(tag["content"])

    # JSON-LD Recipe image
    for tag in soup.find_all("script", type="application/ld+json"):
        raw = tag.string or tag.get_text()
        try:
            data = json.loads(raw)
        except Exception:
            continue

        objects = data if isinstance(data, list) else [data]

        # Handle @graph
        expanded = []
        for obj in objects:
            if isinstance(obj, dict) and isinstance(obj.get("@graph"), list):
                expanded.extend(obj["@graph"])
            else:
                expanded.append(obj)

        for obj in expanded:
            if not isinstance(obj, dict):
                continue

            image = obj.get("image")

            if isinstance(image, str):
                return clean_url(image)

            if isinstance(image, list):
                for item in image:
                    if isinstance(item, str):
                        return clean_url(item)
                    if isinstance(item, dict):
                        u = item.get("url") or item.get("contentUrl")
                        if u:
                            return clean_url(u)

            if isinstance(image, dict):
                u = image.get("url") or image.get("contentUrl")
                if u:
                    return clean_url(u)

    # Conservative HTML fallback
    match = re.search(
        r'https?://[^"\'<>\s]+\.(?:jpg|jpeg|png|webp)(?:\?[^"\'<>\s]*)?',
        html,
        re.I
    )
    return clean_url(match.group(0)) if match else ""

def fetch_one(idx):
    row = df.loc[idx]
    source_url = str(row.get("recipe_source_url", "") or "").strip()

    if not source_url:
        return idx, {
            "status": "no_source_url",
            "image_url": ""
        }

    # Existing cache = already attempted. Do not repeat it.
    key = str(idx)
    if key in cache:
        return idx, cache[key]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/154 Safari/537.36"
        )
    }

    try:
        r = requests.get(
            source_url,
            headers=headers,
            timeout=TIMEOUT,
            allow_redirects=True
        )

        if not r.ok:
            return idx, {
                "status": f"http_{r.status_code}",
                "image_url": ""
            }

        image = extract_image(r.text)

        if image:
            return idx, {
                "status": "found",
                "image_url": image,
                "final_url": r.url
            }

        return idx, {
            "status": "not_found",
            "image_url": "",
            "final_url": r.url
        }

    except requests.RequestException as e:
        return idx, {
            "status": "request_error",
            "image_url": "",
            "error": str(e)[:200]
        }
    except Exception as e:
        return idx, {
            "status": "parse_error",
            "image_url": "",
            "error": str(e)[:200]
        }

# Process only uncached records.
pending = [i for i in target_indices if str(i) not in cache]

already_cached_found = 0
for i in target_indices:
    result = cache.get(str(i), {})
    if result.get("image_url"):
        df.at[i, "image_url"] = result["image_url"]
        df.at[i, "image_source"] = "recipe_source_og_or_jsonld"
        df.at[i, "image_status"] = "source_image_found"
        already_cached_found += 1

print(f"Cached image URLs restored: {already_cached_found}")
print(f"New pages to check: {len(pending)}")
print()

new_found = 0
completed = 0
start_time = time.time()

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = [executor.submit(fetch_one, idx) for idx in pending]

    for future in as_completed(futures):
        idx, result = future.result()
        cache[str(idx)] = result
        completed += 1

        if result.get("image_url"):
            df.at[idx, "image_url"] = result["image_url"]
            df.at[idx, "image_source"] = "recipe_source_og_or_jsonld"
            df.at[idx, "image_status"] = "source_image_found"
            new_found += 1

        if completed % BATCH_SIZE == 0 or completed == len(pending):
            CACHE.write_text(
                json.dumps(cache, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            df.to_csv(OUTPUT, index=False)

            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed else 0
            remaining = len(pending) - completed
            eta = remaining / rate / 60 if rate else 0

            total_found = int((df["image_url"].str.strip() != "").sum())

            print(
                f"{completed}/{len(pending)} new pages checked | "
                f"new images: {new_found} | "
                f"total images in dataset: {total_found}/5615 | "
                f"ETA: ~{eta:.1f} min"
            )

# Final save.
CACHE.write_text(
    json.dumps(cache, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
df.to_csv(OUTPUT, index=False)

total_found = int((df["image_url"].str.strip() != "").sum())
missing = len(df) - total_found

print()
print("=" * 70)
print("IMAGE ENRICHMENT COMPLETE")
print("=" * 70)
print(f"Total recipes:       {len(df)}")
print(f"Images available:    {total_found}")
print(f"Images still missing:{missing}")
print(f"Output:              {OUTPUT}")
print(f"Cache:               {CACHE}")
print("=" * 70)

       