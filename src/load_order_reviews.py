from pathlib import Path
import urllib.parse
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection
DB_USER = os.getenv("DB_USER")
DB_PASS = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))  # escape special chars
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

connection_string = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(connection_string)

# File location
file_path = Path("data/raw/olist_order_reviews_dataset.csv")

# Read CSV
df = pd.read_csv(file_path)
print(f"Rows read from CSV: {len(df)}")

# ✅ Drop duplicate review_id values to avoid PK violation
duplicates = df[df.duplicated(subset=["review_id"], keep="first")]
if not duplicates.empty:
    print(f"Dropping {len(duplicates)} duplicate rows based on review_id.")
    duplicates.to_csv("duplicate_order_reviews.csv", index=False)  # optional log

df = df.drop_duplicates(subset=["review_id"], keep="first")
print(f"Rows after removing duplicates: {len(df)}")

# Convert timestamp columns
timestamp_columns = ["review_creation_date", "review_answer_timestamp"]
for column in timestamp_columns:
    df[column] = pd.to_datetime(df[column], errors="coerce")

# Load into PostgreSQL
df.to_sql(
    name="order_reviews",
    con=engine,
    schema="raw",
    if_exists="append",
    index=False
)

print("Order reviews loaded successfully.")
