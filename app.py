import logging
import math
import os
from typing import Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model import predict

logger = logging.getLogger(__name__)


def _allowed_origins() -> list[str]:
    raw = os.getenv("INTELLIOPS_ALLOWED_ORIGINS", "http://localhost:3001,http://127.0.0.1:3001")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    if any(origin == "*" or not origin.startswith(("https://", "http://")) for origin in origins):
        raise ValueError("INTELLIOPS_ALLOWED_ORIGINS must list explicit HTTP(S) origins")
    return origins


app = FastAPI(title="IntelliOps ML Model Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    features: List[float]


class PredictionResponse(BaseModel):
    prediction: Any


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "intelliops-ml"}


@app.get("/")
def root() -> dict:
    return {"message": "ML Model Service Running"}


@app.post("/predict", response_model=PredictionResponse)
def make_prediction(request: PredictionRequest) -> PredictionResponse:
    if not request.features or not all(math.isfinite(value) for value in request.features):
        raise HTTPException(status_code=422, detail="features must be nonempty finite numbers")
    try:
        result = predict(request.features)
        return PredictionResponse(prediction=result)
    except Exception as exc:
        logger.exception("Model inference failed")
        raise HTTPException(status_code=503, detail="Model inference unavailable") from exc
