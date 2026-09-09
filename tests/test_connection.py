import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env
load_dotenv()

# URL-encode the password to handle special characters like @, #, %, etc.
DB_USER = os.getenv("DB_USER")
DB_PASS = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Build connection string
connection_string = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create engine and test connection
engine = create_engine(connection_string)

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print(" Connection successful, result:", result.scalar())
