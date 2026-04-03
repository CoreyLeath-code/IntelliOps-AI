from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model import predict

app = FastAPI(title="IntelliOps AI Model Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
    try:
        score = predict(request.features)
        return PredictionResponse(prediction=score, model_version="local-iris-binary-v1")
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
