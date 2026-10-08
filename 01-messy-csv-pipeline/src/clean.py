import os

import pandas as pd
from ftfy import fix_text

RAW_PATH = "data/raw/zomato.csv"
OUT_DIR = "data/processed"

TEXT_COLUMNS = [
    "name", "address", "location", "rest_type",
    "cuisines", "dish_liked", "listing_city",
]


def rename_columns(df):
    """Column names SQL-friendly banao."""
    return df.rename(columns={
        "approx_cost(for two people)": "cost_for_two",
        "listed_in(type)": "listing_type",
        "listed_in(city)": "listing_city",
    })


def fix_mojibake(df, columns):
    """Kharab encoding (CafÃ©) theek karo."""
    df = df.copy()
    for col in columns:
        df[col] = df[col].apply(lambda x: fix_text(x) if isinstance(x, str) else x)
    return df


def clean_rate(series):
    """'4.1/5' ya '4.1 /5' -> 4.1. 'NEW' aur '-' NaN ban jate hain."""
    return pd.to_numeric(
        series.str.replace("/5", "", regex=False).str.strip(),
        errors="coerce",
    )


def clean_cost(series):
    """'1,200' -> 1200 (nullable integer)."""
    return pd.to_numeric(
        series.str.replace(",", "", regex=False),
        errors="coerce",
    ).astype("Int64")


def extract_listings(df):
    """Dedupe se pehle listing types alag table mein rakho."""
    return df[["name", "address", "listing_type"]].drop_duplicates()


def dedupe_restaurants(df):
    """Survivorship rule: pehle non-null rate wali row, phir highest votes."""
    df = df.copy()
    df["has_rate"] = df["rate"].notnull()
    return (
        df.sort_values(["has_rate", "votes"], ascending=False)
          .drop_duplicates(subset=["name", "address"], keep="first")
          .drop(columns="has_rate")
    )


def yes_no_to_bool(series):
    """'Yes'/'No' -> True/False."""
    return series.map({"Yes": True, "No": False})


def clean_phone(series):
    """Line break hatao, multiple numbers ko ', ' se jodo."""
    return series.str.replace(r"\s*[\r\n]+\s*", ", ", regex=True).str.strip()


def strip_text(df, columns):
    """Text columns ke aage-peeche ke spaces hatao."""
    df = df.copy()
    for col in columns:
        df[col] = df[col].str.strip()
    return df


def empty_list_to_null(series):
    """'[]' string ko asli null banao."""
    return series.replace("[]", pd.NA)


def clean(raw_df):
    """Poori cleaning pipeline. Returns (restaurants, listings)."""
    df = rename_columns(raw_df)
    df = fix_mojibake(df, ["name", "address"])

    df["rate"] = clean_rate(df["rate"])
    df["cost_for_two"] = clean_cost(df["cost_for_two"])

    listings = extract_listings(df)
    df = dedupe_restaurants(df)

    df["online_order"] = yes_no_to_bool(df["online_order"])
    df["book_table"] = yes_no_to_bool(df["book_table"])
    df["phone"] = clean_phone(df["phone"])
    df = strip_text(df, TEXT_COLUMNS)

    df["menu_item"] = empty_list_to_null(df["menu_item"])
    df["reviews_list"] = empty_list_to_null(df["reviews_list"])
    return df, listings


def main():
    raw = pd.read_csv(RAW_PATH)
    df, listings = clean(raw)

    os.makedirs(OUT_DIR, exist_ok=True)
    df.to_csv(f"{OUT_DIR}/restaurants_clean.csv", index=False)
    listings.to_csv(f"{OUT_DIR}/restaurant_listings.csv", index=False)

    print("SAVED restaurants:", df.shape)
    print("SAVED listings:", listings.shape)
    print("menu_item nulls:", df["menu_item"].isnull().sum())
    print("reviews_list nulls:", df["reviews_list"].isnull().sum())

    back = pd.read_csv(f"{OUT_DIR}/restaurants_clean.csv")
    print("READ BACK shape:", back.shape)
    print(back.dtypes[["rate", "cost_for_two", "online_order", "votes"]])

    print("\nname mein bacha hua kharab:",
          df["name"].str.contains("Ã|Â", regex=True, na=False).sum())
    print("address mein bacha hua kharab:",
          df["address"].str.contains("Ã|Â", regex=True, na=False).sum())
    print(df.loc[df["name"].str.contains("Spa Cuisine", na=False), "name"].tolist())


if __name__ == "__main__":
    main()