import pandas as pd
from typing import Optional


def load_data(path: str, output_path: Optional[str] = None) -> pd.DataFrame:
    """
    This function performs the following operations:
    1. Loads CSV with proper datetime parsing
    2. Sorts data chronologically
    3. Handles missing values using forward fill (financially realistic)
    4. Removes remaining NaN values
    5. Saves cleaned data to CSV
    6. Provides diagnostics on data cleaning
    """

    # STEP A: Load CSV safely with datetime parsing
    print("\n" + "="*60)
    print("DATA LOADING AND CLEANING")
    print("="*60)

    df = pd.read_csv(path)

    # Ensure Date column exists
    if "Date" not in df.columns:
        raise ValueError("CSV must contain a 'Date' column.")

    # Parse Date as datetime
    df["Date"] = pd.to_datetime(df["Date"])

    print(f"\n[LOAD] CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"[LOAD] Date range: {df['Date'].min()} to {df['Date'].max()}")

    # STEP B: Sort data chronologically and reset index
    df = df.sort_values("Date").reset_index(drop=True)
    print(f"[SORT] Data sorted chronologically by Date")

    # STEP C: Report missing values BEFORE cleaning
    print(f"\n[DIAGNOSTICS] Missing values BEFORE cleaning:")
    missing_before = df.isnull().sum()
    if missing_before.sum() > 0:
        print(missing_before[missing_before > 0])
    else:
        print("  None detected")

    # Forward fill missing values (financially realistic)
    # This assumes the most recent price holds until a new trade occurs
    df = df.ffill()
    print(f"\n[CLEAN] Forward fill applied to all columns")

    # Drop remaining NaN values (typically at the beginning if first row(s) were entirely missing)
    initial_rows = len(df)
    df = df.dropna()
    dropped_rows = initial_rows - len(df)

    if dropped_rows > 0:
        print(f"[CLEAN] Dropped {dropped_rows} row(s) with remaining NaN values")
    else:
        print(f"[CLEAN] No rows dropped after forward fill")

    # STEP E: Final diagnostics
    print(f"\n[DIAGNOSTICS] Missing values AFTER cleaning:")
    missing_after = df.isnull().sum()
    if missing_after.sum() > 0:
        print(missing_after[missing_after > 0])
    else:
        print("  None detected ✓")

    print(f"\n[FINAL] Clean dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"[FINAL] Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"[FINAL] {len(df)} trading days available")

    # Save cleaned data to CSV if output_path is specified
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"[SAVE] Clean data saved to '{output_path}'")

    print("="*60 + "\n")

    return df.reset_index(drop=True)


if __name__ == "__main__":
    # Example usage
    df = load_data(r"data\assets.csv", output_path=r"data\assets_clean.csv")
    print("First 5 rows of clean data:")
    print(df.head())
    print("\nLast 5 rows of clean data:")
    print(df.tail())
