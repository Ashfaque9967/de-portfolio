import pandas as pd

df = pd.read_csv('data/raw/zomato.csv')

# ===== PROFILING STARTS =====
print("SHAPE (rows, columns): ")
print(df.shape)

print("\nCOLUMNS:")
print(list(df.columns))

print("\nFIRST 3 ROWS:")
print(df.head(3).T)
# ===== PROFILING ENDS =====

# ===== TYPE CHECKING STARTS =====
print("\nDTYPES:")
print(df.dtypes)

print("\nNULL COUNT:")
print(df.isnull().sum())

print("\nNULL PERCENT:")
print((df.isnull().mean() * 100).round(1))

print("\nFULL DUPLICATE ROWS:", df.duplicated().sum())
print("DUPLICATE URLs:", df.duplicated(subset=["url"]).sum())

print("\nRATE VALUES (top 15)")
print(df["rate"].value_counts(dropna=False).head(15))

print("\nCOST VALUES (top 10):")
print(df["approx_cost(for two people)"].value_counts(dropna=False).head(10))
# ===== TYPE CHECKING ENDS =====