# DevSecOps And Security Checks

Проект использует базовый DevSecOps-подход: security checks встроены в CI pipeline и выполняются автоматически при каждом push или pull request в `main`.

## Что Проверяется

| Проверка | Инструмент | Что Покрывает |
| --- | --- | --- |
| Python dependency audit | `pip-audit` | Известные CVE в Python dependencies из `requirements.txt` |
| Dockerfile lint | `Hadolint` | Best practices и типовые ошибки в Dockerfile |
| Docker image scan | `Trivy` | HIGH/CRITICAL vulnerabilities внутри собранного Docker image |
| Runtime image hardening | Dockerfile | Уменьшение attack surface runtime image |
| Artifact publishing | GHCR | Публикация image только после успешных tests и security checks |

## Где Это Запускается

GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

Порядок security-related шагов:

1. Установка Python dependencies.
2. Запуск tests.
3. `pip-audit` проверяет Python dependencies.
4. `docker compose config --quiet` проверяет Compose config.
5. `Hadolint` проверяет Dockerfile.
6. Docker image собирается.
7. `Trivy` сканирует собранный image.
8. При push в `main` image публикуется в GitHub Container Registry.

Если `pip-audit`, `Hadolint` или `Trivy` находят критичную проблему, pipeline завершается с ошибкой.

## Что Уже Было Найдено И Исправлено

### pip-audit

`pip-audit` нашел CVE в старых версиях `Flask` и `Werkzeug`.

Исправление:

- `Flask` обновлен до безопасной версии;
- `Werkzeug` обновлен до безопасной версии;
- после обновления `pip-audit` вернул `No known vulnerabilities found`.

### Trivy

`Trivy` нашел HIGH vulnerabilities не в коде приложения, а в build/runtime tooling внутри Docker image:

- `wheel`;
- vendored dependency внутри `setuptools`.

Исправление:

- во время build обновляются `pip`, `setuptools`, `wheel`;
- после установки dependencies эти tools удаляются из runtime image;
- runtime container больше не содержит `pip`, `setuptools`, `wheel`.

Проверка на VM:

```text
pip-missing
setuptools-missing
wheel-missing
/usr/local/bin/python: No module named pip
```

## Публикация Artifact

Docker image публикуется в GitHub Container Registry только после успешного прохождения pipeline:

```text
ghcr.io/x2slow4u/my-app:latest
ghcr.io/x2slow4u/my-app:<commit-sha>
```

Для pull request выполняются tests, lint и security scans, но push в registry отключен. Это защищает registry от публикации image из непроверенных изменений.

## Текущий Security Baseline

Текущий baseline:

- dependencies фиксируются в `requirements.txt`;
- vulnerability scanning встроен в CI;
- Dockerfile проверяется линтером;
- Docker image сканируется перед publish;
- runtime image hardened;
- secrets не хранятся в repository;
- GHCR publish выполняется через short-lived `GITHUB_TOKEN`.
