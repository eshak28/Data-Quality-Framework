from sklearn.ensemble import IsolationForest
import numpy as np

def detect_nulls(df, threshold=5):
    issues = {}

    for col in df.columns:
        null_pct = df[col].isnull().mean() * 100
        if null_pct > threshold:
            issues[col] = {
                "null_percentage": round(null_pct, 2),
                "issue": "High missing values"
            }

    return issues

def detect_outliers(df):
    outliers = {}

    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        data = df[[col]].dropna()

        # skip small datasets
        if len(data) < 10:
            continue

        # skip low-variance columns
        if data[col].std() < 1:
            continue

        model = IsolationForest(contamination=0.05, random_state=42)
        preds = model.fit_predict(data)

        outlier_count = list(preds).count(-1)

        if outlier_count > 0:
            outliers[col] = {
                "method": "IsolationForest",
                "count": int(outlier_count)
            }

    return outliers