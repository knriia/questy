# Questy

Questy - backend на FastAPI для трекинга пользовательских активностей, расписаний и записей выполнения.

Проект строится как модульный монолит с вертикальной нарезкой по бизнес-модулям. Каждый модуль хранит свой API-слой, application-сервисы, доменные сущности, инфраструктурные модели и репозитории.

## Стек

- FastAPI
- SQLAlchemy async
- asyncpg
- PostgreSQL
- Alembic
- Dishka
- Docker Compose

## Текущие модули

- `users` - создание пользователей и данные пользовательской идентификации.
- `activities` - описание активностей и расписания активностей.
- `activity_records` - история выполнения или пропуска активностей.

## Запуск

Создайте `.env` с нужными переменными для базы данных, приложения и pgAdmin, затем выполните:

```bash
make build
make up
```

`make build` собирает Docker-образ приложения. Он нужен перед первым запуском, потому что миграции выполняются внутри этого образа.

`make up` поднимает сервисы из `docker-compose.yml`: PostgreSQL, миграции, приложение и pgAdmin. Сервис `app` запускается после успешного применения миграций.

Полезные команды:

- `make help` - показать список доступных команд.
- `make build` - собрать Docker-образы.
- `make up` - запустить контейнеры.
- `make down` - остановить и удалить контейнеры.
- `make logs app` - посмотреть логи сервиса `app`.
- `make ps` - показать запущенные контейнеры.
- `make migrate` - применить миграции.
- `make create_migration <name>` - создать новую Alembic-миграцию.
- `make downgrade` - откатить последнюю миграцию.
- `make rollback_to <revision_id>` - откатиться к конкретной ревизии.

## API

Health checks:

- `GET /health`
- `GET /health/db`

Users:

- `POST /users`

Activities:

- `POST /activities`

Activity schedules:

- `POST /activity_schedules`
- `GET /activity_schedules/due`

Activity records:

- `POST /activity_records`

## Архитектура

Проект использует вертикальные границы модулей:

```text
src/modules/<module>/
├── presentation/
├── application/
├── domain/
└── infrastructure/
```

Ответственность слоев:

- `presentation` - FastAPI routes, request/response DTO.
- `application` - use-cases и orchestration.
- `domain` - сущности, enum-ы, бизнес-состояние.
- `infrastructure` - SQLAlchemy models, repositories, доступ к базе данных.

Направление зависимостей:

```text
presentation -> application -> domain
infrastructure -> domain
```

Реализации репозиториев живут в `infrastructure` и возвращают доменные сущности. HTTP DTO живут в `presentation`. SQLAlchemy models не должны импортироваться в `domain`.

## Соглашения

- Новые бизнес-возможности добавляются внутри `src/modules/*`.
- Взаимодействие между модулями должно быть явным: через application-level contracts или идентификаторы.
- Alembic-миграции хранятся в `migrations/versions`.
- `structure.md` содержит сгенерированное дерево проекта и должен обновляться скриптом, а не вручную.
