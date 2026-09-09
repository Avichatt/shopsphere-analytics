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
file_path = Path("data/raw/olist_geolocation_dataset.csv")


# Read CSV
df = pd.read_csv(file_path)

print(f"Rows read from CSV: {len(df)}")


# Convert numeric columns
numeric_columns = [
    "geolocation_zip_code_prefix",
    "geolocation_lat",
    "geolocation_lng"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# Load into PostgreSQL
df.to_sql(
    name="geolocation",
    con=engine,
    schema="raw",
    if_exists="append",
    index=False
)

print("Geolocation data loaded successfully.")