from __future__ import annotations

import os
from typing import Any, List

import mlflow.pytorch
import torch

_model: Any = None


def _get_model() -> Any:
    global _model
    if _model is None:
        run_id = os.environ.get("MLFLOW_RUN_ID", "<RUN_ID>")
        _model = mlflow.pytorch.load_model(f"runs:/{run_id}/model")
    return _model


def predict(input_data: List[float]) -> List[float]:
    model = _get_model()
    with torch.no_grad():
        tensor = torch.tensor(input_data, dtype=torch.float32)
        output = model(tensor)
        return output.numpy().tolist()
