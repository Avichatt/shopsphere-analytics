from pathlib import Path
import pandas as pd


DATA_DIR = Path("data/raw")


for file in DATA_DIR.glob("*.csv"):
    df = pd.read_csv(file)

    print("=" * 80)
    print(f"FILE: {file.name}")
    print(f"ROWS: {df.shape[0]}")
    print(f"COLUMNS: {df.shape[1]}")
    print("=" * 80)

    print(df.head())
    print()
    print("Columns:", df.columns.tolist())
    print("Data types:\n", df.dtypes)