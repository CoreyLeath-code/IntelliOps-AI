import time
from fastapi import Request
from prometheus_client import Counter, Histogram, Gauge

# L6 Observability Telemetry Matrix
SYSTEM_HEALTH_INDEX = Gauge(
    "intelliops_system_health_ratio",
    "Real-time evaluation score of underlying compute health [0.0 - 1.0]"
)

ANOMALY_DETECTION_LATENCY = Histogram(
    "intelliops_anomaly_detection_latency_seconds",
    "Latency distribution profile for real-time log parsing sequences",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

INCIDENT_RESPONSE_COUNTER = Counter(
    "intelliops_incident_mitigation_total",
    "Total volume of automated runbook webhook dispatches categorized by severity",
    ["severity", "service_target"]
)

class TelemetryMiddleware:
    """High-Performance Prometheus Ingestion Hook to track interface latency profiles."""
    async def __call__(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        
        # Track metric endpoint paths dynamically
        if "/api/v1/analyze" in request.url.path:
            ANOMALY_DETECTION_LATENCY.observe(process_time)
            
        return response
