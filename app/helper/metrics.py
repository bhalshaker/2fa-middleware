# metrics.py
import time
import threading
try:
    import psutil
    _HAS_PSUTIL = True
except Exception:
    psutil = None
    _HAS_PSUTIL = False
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
    if _HAS_PSUTIL and psutil is not None:
        try:
            process = psutil.Process()
            RAM_USAGE.set(process.memory_info().rss / 1024 / 1024)
            # cpu_percent with no interval returns a percentage since last call; it's fine for monitoring
            CPU_USAGE.set(psutil.cpu_percent())
            DISK_USAGE.set(psutil.disk_usage("/").percent)
        except Exception:
            # If psutil fails at runtime, set zeros to avoid crashing
            RAM_USAGE.set(0)
            CPU_USAGE.set(0)
            DISK_USAGE.set(0)
    else:
        # psutil not available; set defaults (0) so metrics still expose without crashing
        RAM_USAGE.set(0)
        CPU_USAGE.set(0)
        DISK_USAGE.set(0)
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
        try:
            response = await call_next(request)
            latency = time.time() - start_time
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)

            # Measure response size safely. Prefer Content-Length header for streaming responses.
            size = None
            content_length = response.headers.get("content-length") if hasattr(response, "headers") else None
            if content_length:
                try:
                    size = int(content_length)
                except (TypeError, ValueError):
                    size = None
            else:
                # Some response types (e.g. StreamingResponse) have no .body attribute.
                body = getattr(response, "body", None)
                if body is not None:
                    try:
                        size = len(body)
                    except Exception:
                        size = None

            if size is not None:
                RESPONSE_SIZE.observe(size)

            # Increment error count for 4xx and 5xx responses
            if getattr(response, "status_code", 0) >= 400:
                # Use string label to avoid Prometheus label type issues
                ERROR_COUNT.labels(status_code=str(getattr(response, "status_code", "unknown"))).inc()

            return response
        except Exception:
            # Count unhandled exceptions as 500
            ERROR_COUNT.labels(status_code="500").inc()
            raise
        finally:
            # Decrement in-progress requests always
            try:
                IN_PROGRESS.dec()
            except Exception:
                # Ensure middleware doesn't crash if Gauge.dec() fails for any reason
                pass

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
