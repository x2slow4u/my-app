import os
import time

import psycopg2
import redis
from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


app = Flask(__name__)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)

REQUESTS_TOTAL = Counter(
    "app_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "app_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


def check_postgres():
    conn = get_db_connection()
    conn.close()


def check_redis():
    redis_client.ping()


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    endpoint = request.path
    latency = time.time() - request.start_time

    REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)

    return response


@app.route("/")
def hello():
    cache_key = "hello_message"
    cached = redis_client.get(cache_key)

    if cached:
        return jsonify(
            {
                "service": "my-app",
                "status": "running",
                "environment": os.getenv("ENV", "development"),
                "message": cached,
                "source": "cache",
            }
        )

    message = f"Hello from my-app! Environment: {os.getenv('ENV', 'development')}"
    redis_client.setex(cache_key, 30, message)
    return jsonify(
        {
            "service": "my-app",
            "status": "running",
            "environment": os.getenv("ENV", "development"),
            "message": message,
            "source": "fresh",
        }
    )


@app.route("/health")
def health():
    return "OK"


@app.route("/ready")
def readiness():
    checks = {
        "app": "ok",
        "postgres": "unknown",
        "redis": "unknown",
    }

    try:
        check_postgres()
        checks["postgres"] = "ok"
    except Exception:
        checks["postgres"] = "error"

    try:
        check_redis()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    status_code = 200 if all(value == "ok" for value in checks.values()) else 503
    return jsonify(checks), status_code


@app.route("/db")
def db_test():
    try:
        check_postgres()
        return "Database connection OK"
    except Exception as e:
        return f"Database connection FAILED: {e}", 500


@app.route("/redis")
def redis_test():
    try:
        check_redis()
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        return f"Redis connection OK. Test value: {value}"
    except Exception as e:
        return f"Redis connection FAILED: {e}", 500


@app.route("/stats")
def stats():
    try:
        info = redis_client.info("stats")
        return jsonify(
            {
                "total_commands_processed": info["total_commands_processed"],
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        )
    except Exception as e:
        return f"Stats error: {e}", 500


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
