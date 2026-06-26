# Security Checks

Проект использует базовый DevSecOps набор проверок в GitHub Actions.

## Что Проверяется

| Проверка | Инструмент | Что покрывает |
| --- | --- | --- |
| Python dependency audit | `pip-audit` | Известные CVE в Python dependencies |
| Dockerfile lint | `Hadolint` | Best practices для Dockerfile |
| Docker image scan | `Trivy` | HIGH/CRITICAL vulnerabilities в Docker image |

## Где Смотреть Результат

Открой вкладку GitHub Actions:

```text
https://github.com/x2slow4u/my-app/actions
```

Workflow должен проходить зеленым статусом. Если `Trivy` или `pip-audit` находят HIGH/CRITICAL проблему, pipeline падает и показывает уязвимую dependency или package.

## Почему Это Важно

Для DevOps-портфолио важно показать не только build/deploy, но и базовое понимание supply chain security:

- зависимости фиксируются в `requirements.txt`;
- Dockerfile проверяется линтером;
- image сканируется перед публикацией или deploy;
- security checks встроены в CI, а не запускаются вручную.
