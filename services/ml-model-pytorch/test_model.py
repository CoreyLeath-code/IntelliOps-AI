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


def test_model_api_rejects_nonfinite_features_without_loading_model():
    """Invalid numerical payloads must be rejected before inference."""
    from fastapi import HTTPException
    import asyncio
    import app as service_app

    for features in ([float("nan"), 1.0, 2.0, 3.0], [float("inf"), 1.0, 2.0, 3.0]):
        try:
            asyncio.run(service_app.make_prediction(service_app.PredictionRequest(features=features)))
        except (HTTPException, ValueError) as exc:
            assert getattr(exc, "status_code", 422) == 422
        else:
            raise AssertionError("nonfinite features unexpectedly accepted")


def test_model_api_hides_internal_exception(monkeypatch):
    from fastapi import HTTPException
    import asyncio
    import app as service_app

    def failing_predict(_features):
        raise RuntimeError("sensitive internal path /private/models")

    monkeypatch.setattr(service_app, "predict", failing_predict)
    try:
        asyncio.run(service_app.make_prediction(service_app.PredictionRequest(features=[1, 2, 3, 4])))
    except HTTPException as exc:
        assert exc.status_code == 503
        assert "sensitive" not in str(exc.detail)
        assert exc.detail == "Model inference unavailable"
    else:
        raise AssertionError("failed inference unexpectedly succeeded")


def test_model_service_cors_disallows_wildcard_credentials():
    from starlette.middleware.cors import CORSMiddleware
    import app as service_app

    cors = next(item for item in service_app.app.user_middleware if item.cls is CORSMiddleware)
    assert "*" not in cors.kwargs["allow_origins"]
    assert cors.kwargs["allow_credentials"] is False
