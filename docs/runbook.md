# Runbook

Практические команды для запуска, проверки, обновления и rollback проекта.

## Запуск

```bash
cp .env.example .env
docker compose up -d --build
```

## Проверка Статуса

```bash
docker compose ps
curl http://localhost:8088/nginx-health
curl http://localhost:5000/health
curl http://localhost:5000/ready
curl http://localhost:5000/metrics
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health
```

## Логи

```bash
docker compose logs -f web
docker compose logs -f nginx
docker compose logs -f prometheus
docker compose logs -f grafana
```

## Обновление На VM

```bash
cd ~/my-app
git pull --ff-only origin main
docker compose up -d --build
docker compose ps
```

## Rollback

1. Найти предыдущий рабочий commit:

```bash
git log --oneline -5
```

2. Переключиться на него:

```bash
git checkout <commit_sha>
docker compose up -d --build
```

3. Вернуться на `main`, когда проблема исправлена:

```bash
git switch main
git pull --ff-only origin main
docker compose up -d --build
```

## Полная Очистка Demo Environment

Команда удаляет containers и volumes, включая данные PostgreSQL, Redis, Prometheus и Grafana.

```bash
docker compose down -v
```
