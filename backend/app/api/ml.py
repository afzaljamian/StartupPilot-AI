
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/api/ml",
    tags=["Machine Learning"]
)

RESULTS_PATH = (
    Path(__file__).resolve().parents[1]
    / "ml"
    / "artifacts"
    / "evaluation_results.json"
)


@router.get("/results")
async def get_ml_results():

    if not RESULTS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="ML evaluation results not found. Train models first."
        )

    try:
        with open(RESULTS_PATH, "r") as file:
            results = json.load(file)

        return {
            "success": True,
            "data": results
        }

    except (OSError, json.JSONDecodeError):
        raise HTTPException(
            status_code=500,
            detail="Unable to read ML evaluation results."
        )
