# Messy CSV Pipeline: Zomato Bangalore Restaurants

Cleaning a messy real-world dataset (51,717 rows) into a normalized PostgreSQL database, with SQL analysis and unit tests.

## Problem

The raw Zomato Bangalore dataset looks usable but is full of hidden problems: ratings stored as text, the same restaurant repeated many times (once per listing category, with slightly different vote counts), corrupted text encoding, and a whole table of reviews packed inside one column. Analysing it directly gives wrong answers (for example, 51,717 "restaurants" when the real number is 12,464).

This project builds a reproducible pipeline that profiles, cleans, models and loads the data, then answers questions with SQL.

## Architecture

```
data/raw/zomato.csv  (never modified)
        |
        v
src/clean.py          -> restaurants_clean.csv, restaurant_listings.csv
src/parse_reviews.py  -> reviews.csv
        |
        v
sql/schema.sql        (tables, primary/foreign keys, index, view)
src/load.py           -> PostgreSQL (restaurants, restaurant_listings, reviews)
        |
        v
sql/analysis.sql      (window functions, EXPLAIN, view, subquery, self-join, transaction)
```

Tech: Python 3.12, pandas, SQLAlchemy, PostgreSQL 18, ftfy, pytest.

## What was messy, and how I fixed it

| Problem | Evidence | Fix |
|---|---|---|
| Rating stored as text | `"4.1/5"` and `"4.1 /5"` (with space), plus `"NEW"` (2,208) and `"-"` (69) | Strip `/5`, convert to float, non-numeric becomes NULL |
| Cost stored as text | `"1,200"` style values, 346 missing | Remove commas, nullable integer |
| Hidden duplicates | 0 exact duplicate rows and 0 duplicate URLs, but 51,717 rows collapse to 12,499 on `name + address` | Dedupe on the business key |
| Duplicates were not identical | Votes differed in 3,936 groups, rating in 1,412 | Survivorship rule: prefer a row with a rating, then highest votes (the highest-votes row of one restaurant had a NULL rating) |
| Corrupted text encoding (mojibake) | `CafÃ©` in 269 rows (65 unique names) and 20 address rows | `ftfy` before dedupe. This exposed 35 more hidden duplicates (12,499 to 12,464) |
| Multi-value phone cells | 4,460 rows with 2+ numbers separated by line breaks | Join with `, ` |
| Empty lists stored as the string `"[]"` | `menu_item` mostly empty, `reviews_list` empty for about 20% | Convert to real NULL |
| Reviews packed in one column | 9,989 cells parsed with 0 failures into 249,703 reviews | Parsed with `ast.literal_eval` into a child `reviews` table |
| Duplicate reviews | 249,703 reviews but only about 108.9K distinct (the same reviews repeat across listing rows) | Dedupe on `name, address, rating, review_text`: 108,945 remain |
| Corruption `ftfy` could not repair | 22,241 of 249,703 raw reviews had mojibake markers, about 1,481 were repaired | Not deleted: flagged with `text_corrupted` (9,293 flagged after review dedupe) |

Cleaning rules are unit tested with pytest (8 tests), including the dedupe rule.

## Key findings (SQL)

- Top 10 restaurants in Indiranagar hold about 25.5% of that area's votes (vote concentration).
- Small locations skew averages, so the location summary view keeps only locations with 20+ restaurants (Lavelle Road ranks first at 4.07).
- An index on `name` cut a lookup from 6.9 ms (Seq Scan, 1,672 buffers) to 0.055 ms (Index Scan, 3 buffers). `LIKE '%text%'` cannot use it and falls back to a Seq Scan.
- After review dedupe, 8 of the top 10 restaurants by review count had an average review rating below their listed rating. I did not find the cause.

## Limitations

- The dataset has no scrape timestamps, review dates or reviewer IDs. Two different people writing the same short review with the same rating are merged into one, and reviews with no text and the same rating also collapse into one.
- About 9.3K reviews still contain corrupted characters after `ftfy` (flagged with `text_corrupted`). Three different ftfy settings gave identical results, so the damage is likely lossy in the source data (not verified).
- Vote counts are probably cumulative, so older restaurants likely have an advantage. Votes measure popularity, not quality.

## How to run

1. Clone the repo and create a virtual environment: `python -m venv venv`, activate it, then `pip install -r requirements.txt`.
2. Download the "Zomato Bangalore Restaurants" dataset from Kaggle and place `zomato.csv` in `data/raw/`.
3. Create a PostgreSQL database named `zomato_db` and a `.env` file with `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.
4. Run in order: `python src/clean.py`, `python src/parse_reviews.py`, `python src/load.py`.
5. Run tests: `pytest`.

Run all commands from inside the `01-messy-csv-pipeline` folder. `load.py` creates the tables from `sql/schema.sql` itself.