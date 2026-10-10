.PHONY: help up down logs restart shell ps build rebuild down-v ps-a migrate create_migration downgrade rollback_to prepare-test-db
.PHONY: test-unit test-integration-no-db test-integration-db

ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
SERVICE := $(firstword $(ARGS))

ifneq ($(ARGS),)
$(ARGS):
	@:
endif

help:
	@echo "Available commands:"
	@echo ""
	@echo "  make up [services...]              Start containers"
	@echo "  make build [services...]           Build containers"
	@echo "  make rebuild [services...]         Rebuild containers without cache"
	@echo "  make down                          Stop and remove containers"
	@echo "  make down-v                        Stop and remove containers with volumes"
	@echo "  make logs [services...]            Show logs"
	@echo "  make restart [services...]         Restart containers"
	@echo "  make shell <service>               Open shell in service"
	@echo "  make ps                            Show running containers"
	@echo "  make ps-a                          Show all containers"
	@echo "  make migrate                       Apply migrations"
	@echo "  make prepare-test-db               Create PostgreSQL role from .env.test"
	@echo "  make test-unit                     Run unit tests locally"
	@echo "  make test-integration-no-db        Run integration tests without a database locally"
	@echo "  make test-integration-db           Run PostgreSQL integration tests in a container"
	@echo "  make downgrade                     Rollback last migration (-1)"
	@echo "  make rollback_to <revision_id>     Rollback to specific revision ID"
	@echo "  make create_migration <name>       Create new alembic migration"
	@echo ""
	@echo "Examples:"
	@echo "  make up"
	@echo "  make up app postgres"
	@echo "  make logs app"
	@echo "  make shell app"
	@echo "  make create_migration init_db"
	@echo "  make migrate"
	@echo "  make downgrade"
	@echo "  make rollback_to 5cef681a714a"

up:
	docker compose up -d $(ARGS)

build:
	docker compose build $(ARGS)

rebuild:
	docker compose build --no-cache $(ARGS)

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f $(ARGS)

restart:
	docker compose restart $(ARGS)

shell:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Ошибка: Укажите имя сервиса. Пример: make shell app"; \
		exit 1; \
	fi
	docker compose exec $(SERVICE) bash

ps:
	docker compose ps

ps-a:
	docker compose ps -a

migrate:
	docker compose run --rm migrations

prepare-test-db:
	.venv/bin/python -m tests.support.prepare_database

test-unit:
	.venv/bin/pytest -q --strict-markers -m unit

test-integration-no-db:
	.venv/bin/pytest -q --strict-markers -m integration_no_db

test-integration-db:
	docker run --rm --network container:app \
		-v "$(CURDIR):/workspace:ro" -w /workspace \
		-e PYTHONPATH=/workspace/.venv/lib/python3.14/site-packages:/workspace/src \
		-e PYTHONDONTWRITEBYTECODE=1 \
		--entrypoint /app/.venv/bin/python \
		questy-app -m pytest -q --strict-markers -p no:cacheprovider -m integration_db

create_migration:
	@if [ -z "$(ARGS)" ]; then \
		echo "Ошибка: укажи название миграции. Пример: make create_migration init_db"; \
		exit 1; \
	fi
	docker compose run --rm migrations alembic revision --autogenerate -m "$(ARGS)"

downgrade:
	docker compose run --rm migrations alembic downgrade -1

rollback_to:
	@if [ -z "$(ARGS)" ]; then \
		echo "Ошибка: укажи ID миграции. Пример: make rollback_to 5cef681a714a"; \
		exit 1; \
	fi
	docker compose run --rm migrations alembic downgrade $(ARGS)
