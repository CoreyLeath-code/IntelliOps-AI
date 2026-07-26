#!/usr/bin/env python3
"""Reproducible benchmark for the deployed IntelliOps PyTorch model path."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import platform
import resource
import statistics
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

SEED = 20260718


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def load_model_module(repo_root: Path):
    path = repo_root / "services" / "ml-model-pytorch" / "model.py"
    spec = importlib.util.spec_from_file_location("intelliops_benchmark_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load model module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=2_000)
    parser.add_argument("--warmup", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("benchmarks/latest.json"))
    args = parser.parse_args()
    if args.iterations < 100 or args.warmup < 10:
        parser.error("iterations must be >= 100 and warmup must be >= 10")

    import numpy as np
    import torch
    from sklearn.datasets import load_iris

    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.set_num_threads(1)
    repo_root = Path(__file__).resolve().parents[1]
    model_module = load_model_module(repo_root)
    iris = load_iris()
    features = iris.data.astype(float).tolist()
    labels = (iris.target == 0).astype(int).tolist()

    tracemalloc.start()
    cold_started = time.perf_counter_ns()
    first_score = model_module.predict(features[0])
    cold_start_ms = (time.perf_counter_ns() - cold_started) / 1_000_000

    for index in range(args.warmup):
        model_module.predict(features[index % len(features)])

    timings_us: list[float] = []
    benchmark_started = time.perf_counter_ns()
    for index in range(args.iterations):
        started = time.perf_counter_ns()
        model_module.predict(features[index % len(features)])
        timings_us.append((time.perf_counter_ns() - started) / 1_000)
    elapsed_s = (time.perf_counter_ns() - benchmark_started) / 1_000_000_000
    _, peak_python_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    predicted = [int(model_module.predict(row) >= 0.5) for row in features]
    tp = sum(actual == 1 and guess == 1 for actual, guess in zip(labels, predicted))
    tn = sum(actual == 0 and guess == 0 for actual, guess in zip(labels, predicted))
    fp = sum(actual == 0 and guess == 1 for actual, guess in zip(labels, predicted))
    fn = sum(actual == 1 and guess == 0 for actual, guess in zip(labels, predicted))
    accuracy = (tp + tn) / len(labels)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    rss_scale = 1024 if sys.platform != "darwin" else 1

    result = {
        "schema_version": 1,
        "benchmark": "intelliops-pytorch-model-service",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "environment": {
            "python": platform.python_version(), "platform": platform.platform(),
            "torch": torch.__version__, "device": "cpu", "cpu_count": os.cpu_count(),
        },
        "protocol": {
            "iterations": args.iterations, "warmup": args.warmup,
            "dataset": "scikit-learn Iris", "evaluation_scope": "training-corpus sanity check",
        },
        "cold_start_ms": cold_start_ms,
        "first_score": first_score,
        "warm_latency_us": {
            "mean": statistics.fmean(timings_us), "median": statistics.median(timings_us),
            "p95": percentile(timings_us, 0.95), "p99": percentile(timings_us, 0.99),
            "min": min(timings_us), "max": max(timings_us),
        },
        "throughput_inferences_s": args.iterations / elapsed_s,
        "memory": {
            "peak_python_tracemalloc_mib": peak_python_bytes / 1_048_576,
            "process_max_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * rss_scale / 1_048_576,
        },
        "quality": {
            "accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1,
            "confusion_matrix": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        },
        "limitations": [
            "Quality is evaluated on the same Iris corpus used by the service's lazy training path; it is a sanity check, not held-out accuracy.",
            "Single-process CPU inference excludes HTTP, Go gateway, container, network, GPU, and concurrent-load overhead.",
            "Maximum RSS includes the Python runtime and imported PyTorch/scikit-learn libraries.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

