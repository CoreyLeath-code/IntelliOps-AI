from fastapi import FastAPI
from model import predict

app = FastAPI()

@app.get("/")
def root():
    return {"message": "ML Model Service Running"}

@app.post("/predict")
def make_prediction(data: dict):
    inputs = data["features"]
    result = predict(inputs)
    return {"prediction": result}
