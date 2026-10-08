import pandas as pd

df = pd.read_csv("data/raw/zomato.csv")

for col in ["name", "address", "location", "cuisines", "dish_liked", "reviews_list"]:
    bad = df[col].astype(str).str.contains("Ã|Â", regex=True)
    print(col, "-> kharab rows:", bad.sum())

bad_names = df.loc[df["name"].str.contains("Ã|Â", regex=True), "name"].drop_duplicates()
print("\nKharab unique names:", len(bad_names))
print(bad_names.head(8).tolist())