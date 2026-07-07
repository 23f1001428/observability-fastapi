from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from collections import deque
import time
import uuid

app = FastAPI()

# Store application start time
START_TIME = time.time()

# Prometheus counter
http_requests = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

# Keep last 500 log entries
logs = deque(maxlen=500)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    # Increment counter for every request
    http_requests.inc()

    # Structured log
    logs.append({
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id
    })

    return response


@app.get("/work")
def work(n: int = 1):
    # Simulate K units of work
    for _ in range(n):
        pass

    return {
        "email": "23f1001428@ds.study.iitm.ac.in",   # Replace if required
        "done": n
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return list(logs)[-limit:]