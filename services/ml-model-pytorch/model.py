from __future__ import annotations

from typing import List

import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris

_model: nn.Module | None = None


class Model(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.fc = nn.Linear(4, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        return torch.sigmoid(self.fc(x))


def _train_if_needed() -> nn.Module:
    global _model
    if _model is not None:
        return _model

    data = load_iris()
    X = torch.tensor(data.data, dtype=torch.float32)
    y = torch.tensor((data.target == 0).astype(float), dtype=torch.float32).view(-1, 1)

    model = Model()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.BCELoss()

    for _ in range(100):
        optimizer.zero_grad()
        out = model(X)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()

    _model = model
    return model


def predict(features: List[float]) -> float:
    model = _train_if_needed()
    with torch.no_grad():
        tensor = torch.tensor(features, dtype=torch.float32)
        out = model(tensor)
        return float(out.item())
