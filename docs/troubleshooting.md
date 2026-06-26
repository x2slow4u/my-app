# Troubleshooting

## `/db` Возвращает Password Authentication Failed

Чаще всего это старый PostgreSQL volume с прежними credentials.

Для demo environment можно пересоздать volumes:

```bash
docker compose down -v
docker compose up -d --build
```

## Grafana Не Показывает Dashboard

Проверить provisioning files:

```bash
docker compose logs grafana
ls docker/grafana/provisioning
ls docker/grafana/dashboards
```

Dashboard должен появиться в folder `DevOps Demo`.

## Prometheus Не Видит Targets

Открыть:

```text
http://localhost:9090/targets
```

Проверить config:

```bash
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml
```

## Nginx Не Отвечает

Проверить health endpoint:

```bash
curl http://localhost:8080/nginx-health
docker compose logs nginx
```

## Docker Compose Не Поднимается После Git Pull

Проверить итоговый config:

```bash
docker compose config --quiet
```

Если менялись volumes или credentials, для demo можно пересоздать stack:

```bash
docker compose down -v
docker compose up -d --build
```
