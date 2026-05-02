import os
import sys

# Ensure the service directory itself is on sys.path so that 'model' resolves
# to services/ml-model-pytorch/model.py (not a stale root-level stub).
sys.path.insert(0, os.path.dirname(__file__))
