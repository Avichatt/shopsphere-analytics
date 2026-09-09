from pathlib import Path
import pandas as pd
import os


DATA_DIR = Path("data/raw")


for file in DATA_DIR.glob("*.csv"):

    print("\n" + "=" * 100)
    print(f"DATASET: {file.name}")
    print("=" * 100)

    df = pd.read_csv(file)

    # Basic information
    print("\n--- SHAPE ---")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    # Column information
    print("\n--- DATA TYPES ---")
    print(df.dtypes)

    # Missing values
    print("\n--- MISSING VALUES ---")
    missing = df.isnull().sum()

    missing_percentage = (
        df.isnull().mean() * 100
    )

    missing_report = pd.DataFrame({
        "missing_count": missing,
        "missing_percentage": missing_percentage
    })

    print(
        missing_report[
            missing_report["missing_count"] > 0
        ].sort_values(
            "missing_percentage",
            ascending=False
        )
    )

    # Duplicate rows
    print("\n--- DUPLICATES ---")
    print(f"Duplicate rows: {df.duplicated().sum()}")

    # Unique values
    print("\n--- UNIQUE VALUES ---")

    for column in df.columns:
        print(
            f"{column}: "
            f"{df[column].nunique(dropna=True)} unique values"
        )

    # Numerical summary
    print("\n--- NUMERICAL SUMMARY ---")
    print(df.describe())

    # Sample records
    print("\n--- SAMPLE DATA ---")
    print(df.head(3))




