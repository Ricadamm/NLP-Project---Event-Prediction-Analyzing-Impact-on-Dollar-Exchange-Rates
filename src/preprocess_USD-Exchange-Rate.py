
import pandas as pd
import os
import sys

# ── Paths ────────────────────────────────────────────────────────────────────
RAW_PATH = os.path.join("data", "raw", "Informasi Kurs Jisdor.xlsx")
OUTPUT_DIR = os.path.join("data", "cleaned")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "usd_idr_jisdor_cleaned.csv")


def load_raw(path: str) -> pd.DataFrame:
    """Load the raw Excel file and extract the data rows."""
    df = pd.read_excel(path, header=None)
    print(f"[1/5] Loaded raw file: {df.shape[0]} rows x {df.shape[1]} columns")
    return df


def extract_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract relevant columns from the raw BI export.
    The raw file has a header section (rows 0-3) followed by data:
      Column 0: Row number (NO)
      Column 1: Date string (Tanggal), e.g. "9/1/2026 12:00:00 AM"
      Column 2: Exchange rate (Kurs), e.g. "17727"
    """
    # Find the header row containing "Tanggal" and "Kurs"
    header_idx = None
    for i, row in df.iterrows():
        vals = [str(v).strip().lower() for v in row.values if pd.notna(v)]
        if "tanggal" in vals:
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("Could not find header row with 'Tanggal' column")

    # Data starts right after header
    data = df.iloc[header_idx + 1:, [1, 2]].copy()
    data.columns = ["date_raw", "rate_raw"]
    data = data.dropna(subset=["date_raw", "rate_raw"])

    print(f"[2/5] Extracted {len(data)} data rows (skipped {header_idx + 1} header rows)")
    return data.reset_index(drop=True)


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse date strings into proper datetime objects."""
    df["date"] = pd.to_datetime(df["date_raw"], format="mixed", dayfirst=False)
    df["date"] = df["date"].dt.normalize()  # remove time component

    invalid = df["date"].isna().sum()
    if invalid > 0:
        print(f"  WARNING: {invalid} rows with unparseable dates (dropped)")
        df = df.dropna(subset=["date"])

    print(f"[3/5] Parsed dates: {df['date'].min().date()} to {df['date'].max().date()}")
    return df


def clean_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert rate column to numeric (float)."""
    df["usd_idr"] = pd.to_numeric(df["rate_raw"], errors="coerce")

    invalid = df["usd_idr"].isna().sum()
    if invalid > 0:
        print(f"  WARNING: {invalid} rows with non-numeric rates (dropped)")
        df = df.dropna(subset=["usd_idr"])

    print(f"[4/5] Cleaned rates: min={df['usd_idr'].min():.2f}, "
          f"max={df['usd_idr'].max():.2f}, mean={df['usd_idr'].mean():.2f}")
    return df


def finalize_and_save(df: pd.DataFrame, output_path: str) -> pd.DataFrame:
    """Sort by date ascending, select final columns, and save."""
    df = df[["date", "usd_idr"]].copy()
    df = df.sort_values("date").reset_index(drop=True)

    # Remove any duplicates (same date)
    dupes = df.duplicated(subset=["date"], keep="first").sum()
    if dupes > 0:
        print(f"  WARNING: Removed {dupes} duplicate dates")
        df = df.drop_duplicates(subset=["date"], keep="first")

    # Format date as YYYY-MM-DD for CSV output
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"[5/5] Saved {len(df)} rows to {output_path}")
    print(f"\n-- Summary ------------------------------------------")
    print(f"  Source:      Bank Indonesia JISDOR")
    print(f"  Currency:    USD/IDR")
    print(f"  Period:      {df['date'].iloc[0]} to {df['date'].iloc[-1]}")
    print(f"  Total days:  {len(df)} trading days")
    print(f"  Note:        Weekends and Indonesian public holidays excluded")
    return df


def main():
    if not os.path.exists(RAW_PATH):
        print(f"ERROR: Raw file not found at '{RAW_PATH}'")
        print("Place 'Informasi Kurs Jisdor.xlsx' in data/raw/ before running.")
        sys.exit(1)

    df = load_raw(RAW_PATH)
    df = extract_data(df)
    df = clean_dates(df)
    df = clean_rates(df)
    df = finalize_and_save(df, OUTPUT_PATH)

    print(f"\nFirst 5 rows:\n{df.head().to_string(index=False)}")
    print(f"\nLast 5 rows:\n{df.tail().to_string(index=False)}")


if __name__ == "__main__":
    main()
