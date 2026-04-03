from model import predict

def test_prediction():
    result = predict([5.1, 3.5, 1.4, 0.2])
    assert result is not None
