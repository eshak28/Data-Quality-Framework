from fastapi import FastAPI
from backend.routes import upload, quality, metadata
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import chat
import pandas as pd
import numpy as np
from scipy import stats


app = FastAPI(title="AI Data Governance Engine")

# Routers
app.include_router(upload.router, prefix="/api")
app.include_router(quality.router, prefix="/api")
app.include_router(metadata.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root
@app.get("/")
def root():
    return {"message": "Data Governance Engine Running"}

def clean_data(df):
    df.replace(["UNKNOWN", "N/A", "", "null", "ERROR"], np.nan, inplace=True)

    for col in ["Quantity", "Price Per Unit", "Total Spent"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def profile_data(df):
    missing = df.isnull().sum()

    worst_column = missing.idxmax()
    worst_count = int(missing.max())

    return {
        "missing_values": missing.to_dict(),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "row_count": len(df),
        "worst_column": worst_column,
        "worst_missing_count": worst_count
    }

def data_quality_checks(df):
    issues = []

    # Missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        issues.append(f"Dataset has {missing} missing values")

    # Logical check
    if all(col in df.columns for col in ["Quantity", "Price Per Unit", "Total Spent"]):
        invalid = df[
            (df["Quantity"] * df["Price Per Unit"] != df["Total Spent"])
        ]
        if len(invalid) > 0:
            issues.append(f"{len(invalid)} rows have incorrect total calculation")

    return issues


def detect_outliers(df):
    try:
        numeric_cols = df.select_dtypes(include=np.number).columns

        if len(numeric_cols) == 0:
            return []

        numeric_df = df[numeric_cols].dropna()

        if len(numeric_df) < 10:
            return []

        z_scores = np.abs(stats.zscore(numeric_df))
        outliers = (z_scores > 2.5).any(axis=1)

        return numeric_df[outliers].head(20).to_dict(orient="records")

    except:
        return []
    
def suggest_fixes(df):
    suggestions = []

    if df.isnull().sum().sum() > 0:
        suggestions.append("Fill missing values using mean/mode")

    if "Total Spent" in df.columns:
        suggestions.append("Recalculate Total Spent = Quantity × Price")

    return suggestions