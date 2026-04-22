from fastapi import APIRouter
from backend.models.schema import Metadata

router = APIRouter()

REQUIRED_FIELDS = ["title", "description", "license"]

@router.post("/validate-metadata")
def validate_metadata(metadata: Metadata):
    missing = [f for f in REQUIRED_FIELDS if getattr(metadata, f) is None]

    if missing:
        return {
            "status": "fail",
            "missing_fields": missing
        }

    return {"status": "pass"}