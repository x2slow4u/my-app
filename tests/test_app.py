import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import app as flask_app_module


@pytest.fixture
def client(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.storage = {}

        def get(self, key):
            return self.storage.get(key)

        def setex(self, key, ttl, value):
            self.storage[key] = value

        def set(self, key, value):
            self.storage[key] = value

        def info(self, section):
            return {
                "total_commands_processed": 1,
                "keyspace_hits": 0,
                "keyspace_misses": 0,
            }

        def ping(self):
            return True

    monkeypatch.setattr(flask_app_module, "redis_client", FakeRedis())
    flask_app_module.app.config.update(TESTING=True)

    with flask_app_module.app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.text == "OK"


def test_root_endpoint_uses_cache(client):
    first_response = client.get("/")
    second_response = client.get("/")

    assert first_response.status_code == 200
    assert first_response.json["service"] == "my-app"
    assert first_response.json["status"] == "running"
    assert first_response.json["source"] == "fresh"
    assert second_response.json["source"] == "cache"


def test_readiness_endpoint(client, monkeypatch):
    monkeypatch.setattr(flask_app_module, "check_postgres", lambda: None)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json["app"] == "ok"
    assert response.json["postgres"] == "ok"
    assert response.json["redis"] == "ok"


def test_metrics_endpoint(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/plain")
    assert b"app_http_requests_total" in response.data
