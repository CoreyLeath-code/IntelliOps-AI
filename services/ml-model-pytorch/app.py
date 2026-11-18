import logging
import math
import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model import predict

logger = logging.getLogger(__name__)


def _allowed_origins() -> list[str]:
    """Allow only explicitly configured browser origins (never wildcard credentials)."""
    raw = os.getenv("INTELLIOPS_ALLOWED_ORIGINS", "http://localhost:3001,http://127.0.0.1:3001")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    if any(origin == "*" or not origin.startswith(("https://", "http://")) for origin in origins):
        raise ValueError("INTELLIOPS_ALLOWED_ORIGINS must list explicit HTTP(S) origins")
    return origins


app = FastAPI(title="IntelliOps AI Model Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    features: List[float] = Field(..., min_length=4, max_length=4)


class PredictionResponse(BaseModel):
    prediction: float
    model_version: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ml-model"}


@app.post("/predict", response_model=PredictionResponse)
def make_prediction(request: PredictionRequest) -> PredictionResponse:
    if not all(math.isfinite(value) for value in request.features):
        raise HTTPException(status_code=422, detail="features must be finite numbers")
    try:
        score = predict(request.features)
        if not math.isfinite(score):
            raise RuntimeError("model returned non-finite prediction")
        return PredictionResponse(prediction=score, model_version="local-iris-binary-v1")
    except Exception as exc:
        logger.exception("Model inference failed")
        raise HTTPException(status_code=503, detail="Model inference unavailable") from exc
