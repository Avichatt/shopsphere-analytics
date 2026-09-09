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
file_path = Path("data/raw/olist_order_payments_dataset.csv")

# Read CSV
df = pd.read_csv(file_path)
print(f"Rows read from CSV: {len(df)}")

# ✅ Filter out invalid rows (installments must be >= 1)
invalid_rows = df[df["payment_installments"] < 1]
if not invalid_rows.empty:
    print(f"Dropping {len(invalid_rows)} rows with invalid installments (0).")
    invalid_rows.to_csv("invalid_payments.csv", index=False)  # optional: keep a record

df = df[df["payment_installments"] >= 1]
print(f"Rows after filtering: {len(df)}")

# Load into PostgreSQL
df.to_sql(
    name="payments",
    con=engine,
    schema="raw",
    if_exists="append",
    index=False
)

print("Payments loaded successfully.")
