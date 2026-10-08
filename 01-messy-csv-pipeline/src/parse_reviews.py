import ast
import logging
import os
import pandas as pd
from ftfy import fix_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

MARKERS = "Ã|Â|â€|ð"

df = pd.read_csv("data/processed/restaurants_clean.csv")
df = df[df["reviews_list"].notnull()]

rows, failed = [], 0
for name, address, cell in zip(df["name"], df["address"], df["reviews_list"]):
    try:
        items = ast.literal_eval(cell)
    except (ValueError, SyntaxError):
        failed += 1
        log.warning("Parse failed for restaurant: %s", name)
        continue
    for rating_str, text in items:
        rows.append((name, address, rating_str, text))

reviews = pd.DataFrame(rows, columns=["name", "address", "rating_raw", "review_text"])
log.info("Parsed %d cells (%d failed), %d reviews", len(df) - failed, failed, len(reviews))

# rating: "Rated 4.0" -> 4.0 (None rating null hi rahegi)
reviews["rating"] = pd.to_numeric(
    reviews["rating_raw"].str.replace("Rated", "", regex=False).str.strip(),
    errors="coerce",
)

# text: "RATED" prefix hatao
text = reviews["review_text"].str.replace(r"^RATED\s*", "", regex=True).str.strip()

# ftfy sirf marker wali rows pe
mask = text.str.contains(MARKERS, regex=True, na=False)
log.info("Mojibake candidates: %d", mask.sum())
text.loc[mask] = text.loc[mask].apply(fix_text)

# fix ke baad bhi kharab rows ko flag karo, delete nahi
reviews["text_corrupted"] = text.str.contains(MARKERS, regex=True, na=False)

# khaali text ko asli NULL banao
reviews["review_text"] = text.replace("", pd.NA)
reviews = reviews.drop(columns="rating_raw")

# duplicate reviews hatao (snapshots mein wahi review repeat hua tha)
before = len(reviews)
reviews = reviews.drop_duplicates(
    subset=["name", "address", "rating", "review_text"]
).reset_index(drop=True)
log.info("Review dedupe: %d -> %d (%d hataye)", before, len(reviews), before - len(reviews))

os.makedirs("data/processed", exist_ok=True)
reviews.to_csv("data/processed/reviews.csv", index=False)

print("Reviews saved:", reviews.shape)
print("Rating nulls:", reviews["rating"].isnull().sum())
print("Review text nulls:", reviews["review_text"].isnull().sum())
print("text_corrupted True:", reviews["text_corrupted"].sum())