from typing import Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model import predict

app = FastAPI(title="IntelliOps ML Model Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    try:
        result = predict(request.features)
        return PredictionResponse(prediction=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
