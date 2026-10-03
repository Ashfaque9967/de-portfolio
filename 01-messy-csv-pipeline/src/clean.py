import pandas as pd

df = pd.read_csv("data/raw/zomato.csv")

# 1. Column names SQL-friendly
df = df.rename(columns={
    "approx_cost(for two people)": "cost_for_two",
    "listed_in(type)": "listing_type",
    "listed_in(city)": "listing_city",
})

# 2. rate: "4.1/5" ya "4.1 /5" -> 4.1 (NEW aur "-" NaN ban jayenge)
df["rate"] = pd.to_numeric(
    df["rate"].str.replace("/5", "", regex=False).str.strip(),
    errors="coerce",
)

# 3. cost_for_two: "1,200" -> 1200
df["cost_for_two"] = pd.to_numeric(
    df["cost_for_two"].str.replace(",", "", regex=False),
    errors="coerce",
).astype("Int64")

# 4. Listing types alag rakho, phir dedupe
listings = df[["name", "address", "listing_type"]].drop_duplicates()

df["has_rate"] = df["rate"].notnull()
df = (
    df.sort_values(["has_rate", "votes"], ascending=False)
      .drop_duplicates(subset=["name", "address"], keep="first")
      .drop(columns="has_rate")
)

# 5. Yes/No -> True/False
df["online_order"] = df["online_order"].map({"Yes": True, "No": False})
df["book_table"] = df["book_table"].map({"Yes": True, "No": False})

# 6. phone: line break hatao
df["phone"] = df["phone"].str.replace(r"\s*[\r\n]+\s*", ", ", regex=True).str.strip()

# 7. Text columns ke extra spaces hatao
for col in ["name", "address", "location", "rest_type", "cuisines", "dish_liked", "listing_city"]:
    df[col] = df[col].str.strip()

# 8. "[]" ko asli null banao
df["menu_item"] = df["menu_item"].replace("[]", pd.NA)
df["reviews_list"] = df["reviews_list"].replace("[]", pd.NA)

# 9. Cleaned data save karo (raw file ko haath nahi lagaya)
import os
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/restaurants_clean.csv", index=False)
listings.to_csv("data/processed/restaurant_listings.csv", index=False)

# Checks
print("SAVED restaurants:", df.shape)
print("SAVED listings:", listings.shape)
print("menu_item nulls:", df["menu_item"].isnull().sum())
print("reviews_list nulls:", df["reviews_list"].isnull().sum())

back = pd.read_csv("data/processed/restaurants_clean.csv")
print("READ BACK shape:", back.shape)
print(back.dtypes[["rate", "cost_for_two", "online_order", "votes"]])