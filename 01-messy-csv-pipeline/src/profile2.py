import pandas as pd

df = pd.read_csv("data/raw/zomato.csv")

print("DUP on name+address:", df.duplicated(subset=["name", "address"]).sum())
print("UNIQUE name+address:", df.drop_duplicates(subset=["name", "address"]).shape[0])

print("\nSAMPLE DUPLICATES:")
dups = df[df.duplicated(subset=["name", "address"], keep=False)]
print(dups.sort_values(["name", "address"])[["name", "listed_in(type)", "votes"]].head(8))

print("\nRATE values that are not like 3.9/5 or 3.9 /5:")
r = df["rate"].dropna()
print(r[~r.str.match(r"^\d\.\d\s?/5$")].value_counts())

print("\nCOST values that are not plain numbers:")
c = df["approx_cost(for two people)"].dropna()
print(c[~c.str.match(r"^\d+$")].value_counts().head(10))