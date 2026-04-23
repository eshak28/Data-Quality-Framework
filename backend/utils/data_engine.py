import pandas as pd
import numpy as np
from scipy import stats

# =========================
# 1. CLEAN DATA
# =========================
def clean_data(df):
    # Replace fake nulls
    df.replace(["UNKNOWN", "N/A", "", "null"], np.nan, inplace=True)

    # Convert numeric columns safely
    for col in ["Quantity", "Price Per Unit", "Total Spent"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


# =========================
# 2. PROFILE DATA
# =========================
def profile_data(df):
    return {
        "missing_values": df.isnull().sum().to_dict(),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "row_count": len(df)
    }


# =========================
# 3. DATA QUALITY CHECKS
# =========================
def data_quality_checks(df):
    issues = []

    # Missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        issues.append(f"Dataset has {missing} missing values")

    # Logical consistency check
    if all(col in df.columns for col in ["Quantity", "Price Per Unit", "Total Spent"]):
        invalid = df[
            (df["Quantity"] * df["Price Per Unit"] != df["Total Spent"])
        ]
        if len(invalid) > 0:
            issues.append(f"{len(invalid)} rows have incorrect total calculation")

    return issues


# =========================
# 4. OUTLIER DETECTION
# =========================
def detect_outliers(df):
    try:
        numeric_cols = [col for col in ["Quantity", "Price Per Unit"] if col in df.columns]

        if len(numeric_cols) == 0:
            return []

        numeric_df = df[numeric_cols].dropna()

        if len(numeric_df) == 0:
            return []

        z_scores = np.abs(stats.zscore(numeric_df))
        outliers = (z_scores > 3).any(axis=1)

        return numeric_df[outliers].to_dict(orient="records")

    except Exception:
        return []


# =========================
# 5. SUGGEST FIXES
# =========================
def suggest_fixes(df):
    suggestions = []

    if df.isnull().sum().sum() > 0:
        suggestions.append("Fill missing values using mean/mode")

    if "Total Spent" in df.columns:
        suggestions.append("Recalculate Total Spent = Quantity × Price")

    if "Payment Method" in df.columns:
        suggestions.append("Fill missing Payment Method using most frequent value")

    return suggestions

def apply_fixes(df):
    df = df.copy()

    # Fill numeric columns with mean
    for col in df.select_dtypes(include=np.number).columns:
        df[col].fillna(df[col].mean(), inplace=True)

    # Fill categorical columns with mode
    for col in df.select_dtypes(include='object').columns:
        if not df[col].mode().empty:
            df[col].fillna(df[col].mode()[0], inplace=True)

    # Recalculate Total Spent
    if all(c in df.columns for c in ["Quantity", "Price Per Unit", "Total Spent"]):
        df["Total Spent"] = df["Quantity"] * df["Price Per Unit"]

    return df