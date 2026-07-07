from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid
import json
from collections import deque

app = FastAPI()

START_TIME = time.time()

REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

logs = deque(maxlen=500)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    REQUEST_COUNTER.inc()

    logs.append(
        {
            "level": "INFO",
            "ts": time.time(),
            "path": request.url.path,
            "request_id": request_id,
        }
    )

    return response


@app.get("/work")
def work(n: int = 1):
    total = 0
    for _ in range(n):
        total += 1

    return {
        "email": "23f1001428@ds.study.iitm.ac.in",
        "done": total
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST,
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