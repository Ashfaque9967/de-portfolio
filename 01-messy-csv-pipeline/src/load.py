import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
engine = create_engine(url)

restaurants = pd.read_csv("data/processed/restaurants_clean.csv")
restaurants["cost_for_two"] = restaurants["cost_for_two"].astype("Int64")
listings = pd.read_csv("data/processed/restaurant_listings.csv")

restaurants.to_sql("restaurants", engine, if_exists="replace", index=False, chunksize=1000)
listings.to_sql("restaurant_listings", engine, if_exists="replace", index=False, chunksize=1000)

reviews = pd.read_csv("data/processed/reviews.csv")
reviews.to_sql("reviews", engine, if_exists="replace", index=False, chunksize=5000)

with engine.connect() as conn:
    for t in ["restaurants", "restaurant_listings", "reviews"]:
        print(t, "rows:", conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar())