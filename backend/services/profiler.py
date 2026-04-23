import pandas as pd

def profile_data(df):
    profile = {}

    for col in df.columns:
        col_data = df[col]

        profile[col] = {
            "dtype": str(col_data.dtype),
            "null_count": int(col_data.isnull().sum()),
            "unique": int(col_data.nunique())
        }

        if pd.api.types.is_numeric_dtype(col_data):
            profile[col].update({
                "mean": float(col_data.mean()),
                "min": float(col_data.min()),
                "max": float(col_data.max())
            })

    correlation = df.corr(numeric_only=True).to_dict()

    return {
        "columns": profile,
        "correlation": correlation,
        "rows": len(df),
        "duplicates": int(df.duplicated().sum())
    }