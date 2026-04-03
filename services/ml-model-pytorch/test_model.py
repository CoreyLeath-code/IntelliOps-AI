from unittest.mock import MagicMock, patch

import torch

import model as model_module


def test_prediction_returns_list():
    """Test that predict returns a non-empty list."""
    mock_output = torch.tensor([0.8])
    mock_model = MagicMock(return_value=mock_output)

    with patch.object(model_module, "_get_model", return_value=mock_model):
        result = model_module.predict([5.1, 3.5, 1.4, 0.2])

    assert isinstance(result, list)
    assert len(result) > 0


def test_prediction_values_are_floats():
    """Test that prediction output values are floats."""
    mock_output = torch.tensor([0.3])
    mock_model = MagicMock(return_value=mock_output)

    with patch.object(model_module, "_get_model", return_value=mock_model):
        result = model_module.predict([4.6, 3.1, 1.5, 0.2])

    assert all(isinstance(v, float) for v in result)


def test_prediction_output_in_range():
    """Test that sigmoid-activated output is within [0, 1]."""
    mock_output = torch.tensor([0.65])
    mock_model = MagicMock(return_value=mock_output)

    with patch.object(model_module, "_get_model", return_value=mock_model):
        result = model_module.predict([5.0, 3.0, 1.6, 0.3])

    assert 0.0 <= result[0] <= 1.0
