from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import pandas as pd
import json
import numpy as np
import io

# ✅ IMPORT ALL FUNCTIONS
from backend.utils.data_engine import (
    clean_data,
    profile_data,
    data_quality_checks,
    detect_outliers,
    suggest_fixes,
    apply_fixes
)

router = APIRouter()


# =========================
# 📊 UPLOAD + ANALYZE
# =========================
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 1. LOAD FILE
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file, low_memory=False)

        elif file.filename.endswith(".json"):
            data = json.load(file.file)

            if isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                df = pd.DataFrame(data)

        else:
            return {"error": "Unsupported file type"}

        # 2. CLEAN BASE DATA
        df = clean_data(df)

        # 3. GOVERNANCE ENGINE
        profile = profile_data(df)
        issues = data_quality_checks(df)
        outliers = detect_outliers(df)
        suggestions = suggest_fixes(df)

        # 4. PREVIEW
        preview = df.head(50).replace({np.nan: None}).to_dict(orient="records")

        # 5. QUALITY SCORE
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()

        quality_score = 0 if total_cells == 0 else round(
            100 - (missing_cells / total_cells) * 100, 2
        )

        # 6. RESPONSE
        return {
            "profile": profile,
            "issues": issues,
            "outliers": outliers,
            "suggestions": suggestions,
            "quality_score": quality_score,
            "preview": preview
        }

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return {"error": str(e)}


# =========================
# 🧹 APPLY FIXES + RETURN CLEANED DATA
# =========================
@router.post("/clean")
async def clean_file(file: UploadFile = File(...)):
    try:
        filename = file.filename

        # LOAD FILE
        if filename.endswith(".csv"):
            df = pd.read_csv(file.file, low_memory=False)
            file_type = "csv"

        elif filename.endswith(".json"):
            data = json.load(file.file)

            if isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                df = pd.DataFrame(data)

            file_type = "json"

        else:
            return {"error": "Unsupported file type"}

        # APPLY PIPELINE
        df = clean_data(df)
        df = apply_fixes(df)

        # RETURN SAME FORMAT
        if file_type == "csv":
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)

            return StreamingResponse(
                buffer,
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=cleaned_data.csv"
                }
            )

        else:
            cleaned = df.replace({np.nan: None}).to_dict(orient="records")

            return {
                "cleaned_data": cleaned
            }

    except Exception as e:
        print("CLEAN ERROR:", str(e))
        return {"error": str(e)}