from fastapi import APIRouter
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict

from backend.services.profiler import profile_data
from backend.services.quality_checker import detect_nulls, detect_outliers
from backend.services.ai_suggester import suggest_fixes, auto_clean

router = APIRouter()

class DataInput(BaseModel):
    data: List[Dict]

@router.post("/analyze")
def analyze(input_data: DataInput):
    df = pd.DataFrame(input_data.data)

    return {
        "profile": profile_data(df),
        "null_issues": detect_nulls(df),
        "outliers": detect_outliers(df),
        "suggestions": suggest_fixes(df)
    }

@router.post("/auto-clean")
def clean_data(input_data: DataInput):
    df = pd.DataFrame(input_data.data)
    cleaned_df = auto_clean(df)

    return {
        "cleaned_data": cleaned_df.to_dict(orient="records")
    }