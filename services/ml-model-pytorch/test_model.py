"""Unit tests for services/ml-model-pytorch/model.py."""
from unittest.mock import MagicMock, patch

import torch

import model as model_module


def test_predict_returns_float():
    """predict() should return a single Python float."""
    mock_model = MagicMock(return_value=torch.tensor([0.8]))

    with patch.object(model_module, "_train_if_needed", return_value=mock_model):
        result = model_module.predict([5.1, 3.5, 1.4, 0.2])

    assert isinstance(result, float)


def test_predict_output_in_range():
    """Sigmoid output must be in [0, 1]."""
    mock_model = MagicMock(return_value=torch.tensor([0.65]))

    with patch.object(model_module, "_train_if_needed", return_value=mock_model):
        result = model_module.predict([5.0, 3.0, 1.6, 0.3])

    assert 0.0 <= result <= 1.0


def test_predict_low_score():
    """Model can return a value close to 0."""
    mock_model = MagicMock(return_value=torch.tensor([0.1]))

    with patch.object(model_module, "_train_if_needed", return_value=mock_model):
        result = model_module.predict([4.6, 3.1, 1.5, 0.2])

    assert 0.0 <= result <= 1.0
