# Alerts

Prometheus alert rules находятся в `docker/prometheus/rules/app-alerts.yml`.

Alertmanager configuration находится в `docker/alertmanager/alertmanager.yml`.

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

## Alert Routing

Prometheus отвечает за вычисление alert rules, а Alertmanager отвечает за группировку, дедупликацию и routing alerts.

Текущий route:

```text
Prometheus rules -> Alertmanager :9093 -> default-receiver
```

`default-receiver` используется как базовый receiver для demo environment. В production вместо него обычно подключается Slack, Telegram, email, PagerDuty или webhook endpoint.

## Проверка Rules

После запуска проекта открой:

```text
http://localhost:9090/rules
http://localhost:9090/alerts
http://localhost:9093
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

Проверить, что Prometheus видит Alertmanager:

```text
http://localhost:9090/status
```
