import pandas as pd

df = pd.read_csv("data/processed/restaurants_clean.csv")
df = df[df["reviews_list"].notnull()]

cell = df["reviews_list"].iloc[0]
print("TYPE:", type(cell))
print("LENGTH:", len(cell))
print("\nSTART:\n", cell[:400])
print("\nEND:\n", cell[-150:])

print("\nCells jisme 'Ã' hai:", df["reviews_list"].str.contains("Ã", regex=False).sum())