import os

import psycopg2
import redis
from flask import Flask, jsonify
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest


app = Flask(__name__)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)

REQUESTS_TOTAL = Counter("myapp_requests_total", "Total HTTP requests")


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


@app.route("/")
def hello():
    cache_key = "hello_message"
    cached = redis_client.get(cache_key)

    if cached:
        return f"{cached} (from cache)"

    message = f"Hello from my-app! Environment: {os.getenv('ENV', 'development')}"
    redis_client.setex(cache_key, 30, message)
    return f"{message} (fresh)"


@app.route("/health")
def health():
    return "OK"


@app.route("/db")
def db_test():
    try:
        conn = get_db_connection()
        conn.close()
        return "Database connection OK"
    except Exception as e:
        return f"Database connection FAILED: {e}", 500


@app.route("/redis")
def redis_test():
    try:
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
    REQUESTS_TOTAL.inc()
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
