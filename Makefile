COMPOSE=docker compose
PYTHON=python

.PHONY: up down restart logs ps test check build clean

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

test:
	$(PYTHON) -m pytest -q

check:
	$(PYTHON) -m py_compile app/app.py
	$(COMPOSE) config --quiet

build:
	$(COMPOSE) build

clean:
	$(COMPOSE) down -v
