# DevSecOps And Security Checks

Проект использует базовый DevSecOps-подход: security checks встроены в CI pipeline и выполняются автоматически при каждом push или pull request в `main`.

Цель не в том, чтобы “поставить галочку”, а в том, чтобы не пропускать в main код, Dockerfile или Docker image с очевидными проблемами.

## Что Проверяется

| Проверка | Инструмент | Что Покрывает |
| --- | --- | --- |
| Python dependency audit | `pip-audit` | Известные CVE в Python dependencies из `requirements.txt` |
| Dockerfile lint | `Hadolint` | Best practices и типовые ошибки в Dockerfile |
| Docker image scan | `Trivy` | HIGH/CRITICAL vulnerabilities внутри собранного Docker image |
| Runtime image hardening | Dockerfile | Уменьшение attack surface runtime image |

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

## Почему Удаление pip/setuptools/wheel Полезно

`pip`, `setuptools` и `wheel` нужны для установки dependencies на этапе build, но приложению в runtime они не нужны.

Удаление этих tools:

- уменьшает attack surface;
- уменьшает количество packages, которые может найти scanner;
- снижает риск supply chain атак внутри runtime container;
- делает image ближе к production-подходу.

## Что Такое Supply Chain Security

Supply chain security - это защита цепочки поставки ПО: dependencies, build tools, container image, CI/CD pipeline и registry.

Для DevOps это важно, потому что уязвимость может быть не только в коде приложения, но и в:

- Python package;
- base image;
- system package внутри image;
- Dockerfile;
- CI/CD action;
- registry credentials;
- runtime tooling.

## Почему Это Полезно Для Портфолио

Этот блок показывает, что проект закрывает не только запуск инфраструктуры, но и базовую security maturity:

- dependencies фиксируются в `requirements.txt`;
- vulnerability scanning встроен в CI;
- Dockerfile проверяется линтером;
- Docker image сканируется перед deploy/publish;
- runtime image hardened;
- secrets не хранятся в repository;
- security checks подтверждаются зеленым GitHub Actions run.

## Как Объяснить На Собеседовании

Короткий ответ:

> Я добавил DevSecOps checks в GitHub Actions: `pip-audit` проверяет Python dependencies, `Hadolint` проверяет Dockerfile, `Trivy` сканирует Docker image. Когда scanners нашли CVE в Flask/Werkzeug и runtime tooling, я обновил dependencies и hardened Docker image: удалил `pip`, `setuptools`, `wheel` после установки packages. Теперь pipeline падает, если появляются HIGH/CRITICAL vulnerabilities.

Более подробный ответ:

> Я хотел показать, что CI/CD pipeline должен проверять не только tests и build, но и безопасность artifact. Поэтому после tests запускается dependency audit, Dockerfile lint и image scan. Это помогает ловить проблемы до deploy. В проекте Trivy показал, что scanner может находить vulnerabilities не только в application dependencies, но и в tools внутри image. Я исправил это через runtime image hardening.

## Ограничения Текущего Подхода

Это базовый DevSecOps уровень, а не полный enterprise security process.

Что пока не сделано:

- нет SBOM artifact;
- нет image signing;
- нет policy enforcement через OPA/Conftest;
- нет Dependabot configuration;
- image пока не публикуется в GHCR;
- нет protected branch rules в repository settings.

## Следующие Улучшения

- Publish Docker image в GHCR после successful security scans.
- Добавить SBOM generation через Trivy или Syft.
- Добавить Dependabot для Python dependencies и GitHub Actions.
- Добавить branch protection rule: запрет merge без зеленого CI.
- Добавить image signing через Cosign.
