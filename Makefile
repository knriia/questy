.PHONY: up down logs restart shell ps

SERVICE := $(word 2,$(MAKECMDGOALS))
ifneq ($(SERVICE),)
$(SERVICE):
	@:
endif

%:
	@:

up:
	docker compose up -d $(SERVICE)

build:
	docker compose build $(SERVICE)

rebuild:
	docker compose build --no-cache $(SERVICE)

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f $(SERVICE)

restart:
	docker compose restart $(SERVICE)

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
