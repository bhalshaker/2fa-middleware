# metrics.py
import time
import psutil
import threading
from prometheus_client import (
    Counter, Gauge, Histogram, make_asgi_app
)
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# System-level metrics
RAM_USAGE = Gauge("ram_usage_mb", "RAM usage in MB")
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage")
DISK_USAGE = Gauge("disk_usage_percent", "Disk usage percentage")
THREAD_COUNT = Gauge("thread_count", "Number of active threads")

# App-level metrics
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency in seconds", ["method", "endpoint"])
REQUEST_COUNT = Counter("request_count_total", "Total number of requests", ["method", "endpoint"])
ERROR_COUNT = Counter("error_count_total", "Total number of error responses", ["status_code"])
RESPONSE_SIZE = Histogram("response_size_bytes", "Size of responses in bytes")
IN_PROGRESS = Gauge("in_progress_requests", "Number of requests in progress")

def update_system_metrics():
    """Update system-level metrics."""
    # Get current process information
    process = psutil.Process()
    RAM_USAGE.set(process.memory_info().rss / 1024 / 1024)
    CPU_USAGE.set(psutil.cpu_percent())
    DISK_USAGE.set(psutil.disk_usage("/").percent)
    THREAD_COUNT.set(threading.active_count())

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect and expose Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        # Update system metrics
        update_system_metrics()
        method = request.method
        endpoint = request.url.path
        # Increment request count
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        # Track in-progress requests
        IN_PROGRESS.inc()
        # Measure request latency
        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
        # Measure response size
        RESPONSE_SIZE.observe(len(response.body or b""))
        # Increment error count for 4xx and 5xx responses
        if response.status_code >= 400:
            ERROR_COUNT.labels(status_code=response.status_code).inc()
        # Decrement in-progress requests
        IN_PROGRESS.dec()
        return response

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
