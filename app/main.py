from fastapi import FastAPI
from prometheus_client import make_asgi_app
from app.metrics import TelemetryMiddleware

app = FastAPI(title="IntelliOps-AI Platform")

# Mount your clean Prometheus tracking endpoint for scraping metrics (/metrics)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Register the custom high-throughput execution timer middleware
app.middleware("http")(TelemetryMiddleware())

@app.post("/api/v1/analyze")
async def process_telemetry_payload(data: dict):
    # Core inference profiling loops go here
    return {"status": "processed", "anomaly_detected": False}
