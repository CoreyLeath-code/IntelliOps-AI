import mlflow.pytorch
import torch

# Load latest model
model = mlflow.pytorch.load_model("runs:/<RUN_ID>/model")

def predict(input_data):
    with torch.no_grad():
        tensor = torch.tensor(input_data, dtype=torch.float32)
        output = model(tensor)
        return output.numpy().tolist()
