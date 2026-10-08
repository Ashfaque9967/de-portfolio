import ast
import pandas as pd
from ftfy import fix_text, fix_encoding

df = pd.read_csv("data/processed/restaurants_clean.csv")
df = df[df["reviews_list"].notnull()]

rows = []
for cell in df["reviews_list"]:
    for rating_str, text in ast.literal_eval(cell):
        rows.append((rating_str, text))
raw = pd.DataFrame(rows, columns=["rating_raw", "text"])

print("Rating None/NaN (raw mein):", raw["rating_raw"].isnull().sum())

raw["text"] = raw["text"].str.replace(r"^RATED\s*", "", regex=True).str.strip()

pat = "Ã|Â|â€|ð"
cand = raw[raw["text"].str.contains(pat, regex=True) | (raw["text"].str.len() <= 10)].copy()
print("Candidate rows:", len(cand))

cand["A"] = cand["text"].apply(fix_text)
cand["B"] = cand["text"].apply(fix_encoding)
cand["C"] = cand["text"].apply(lambda x: fix_text(x, uncurl_quotes=False))

print("\nBache hue marker (kam = behtar):")
print("Bina fix:", cand["text"].str.contains(pat, regex=True).sum())
print("A fix_text (abhi wala):", cand["A"].str.contains(pat, regex=True).sum())
print("B fix_encoding:", cand["B"].str.contains(pat, regex=True).sum())
print("C fix_text uncurl_quotes=False:", cand["C"].str.contains(pat, regex=True).sum())

print("\nEmpty text:")
print("Raw:", (cand["text"] == "").sum())
for col in ["A", "B", "C"]:
    print(col, ":", (cand[col].str.strip() == "").sum())

gone = cand[(cand["text"] != "") & (cand["A"].str.strip() == "")]
print("\nA ne mita diye (raw non-empty):", len(gone))
for t in gone["text"].head(5):
    print(repr(t[:60]))