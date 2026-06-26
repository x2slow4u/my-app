# Alerts

Prometheus alert rules находятся в `docker/prometheus/rules/app-alerts.yml`.

## Настроенные Alerts

| Alert | Условие | Severity |
| --- | --- | --- |
| `AppDown` | `web-app` недоступен больше 1 минуты | critical |
| `HighErrorRate` | 5xx больше 5% за 5 минут | warning |
| `HighLatency` | p95 latency выше 500ms больше 5 минут | warning |
| `PostgresExporterDown` | `postgres-exporter` недоступен | critical |
| `RedisExporterDown` | `redis-exporter` недоступен | critical |
| `HighHostCPUUsage` | CPU host выше 80% больше 5 минут | warning |
| `HighHostMemoryUsage` | RAM host выше 85% больше 5 минут | warning |

## Проверка Rules

После запуска проекта открой:

```text
http://localhost:9090/rules
http://localhost:9090/alerts
```

## Failure Simulation

Проверить `AppDown`:

```bash
docker compose stop web
```

Вернуть сервис:

```bash
docker compose start web
```

Проверить exporter alert:

```bash
docker compose stop redis-exporter
docker compose start redis-exporter
```
