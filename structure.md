questy/
├── src/
│   ├── entrypoints/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── container.py
│   │   ├── scheduler.py
│   │   └── worker.py
│   ├── integrations/
│   │   ├── telegram/
│   │   │   ├── di.py
│   │   │   └── sender.py
│   │   └── __init__.py
│   ├── modules/
│   │   ├── activities/
│   │   │   ├── application/
│   │   │   │   ├── services/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── activity.py
│   │   │   │   │   ├── activity_schedule.py
│   │   │   │   │   ├── activity_schedule_dispatcher.py
│   │   │   │   │   └── activity_schedule_task_sender.py
│   │   │   │   └── __init__.py
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── activity.py
│   │   │   │   │   └── activity_schedule.py
│   │   │   │   └── __init__.py
│   │   │   ├── infrastructure/
│   │   │   │   ├── mappers/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── activity.py
│   │   │   │   │   └── activity_schedule.py
│   │   │   │   ├── models/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── activity.py
│   │   │   │   │   └── activity_schedule.py
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── activity.py
│   │   │   │   │   └── activity_schedule.py
│   │   │   │   └── __init__.py
│   │   │   ├── presentation/
│   │   │   │   ├── dto/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── activity.py
│   │   │   │   │   ├── activity_schedule.py
│   │   │   │   │   └── activity_schedule_notification.py
│   │   │   │   ├── mappers/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── activity.py
│   │   │   │   │   └── activity_schedule.py
│   │   │   │   ├── routes/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── activity.py
│   │   │   │   │   └── activity_schedule.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── tasks.py
│   │   │   ├── __init__.py
│   │   │   ├── di.py
│   │   │   └── enums.py
│   │   ├── activity_records/
│   │   │   ├── application/
│   │   │   │   └── service.py
│   │   │   ├── domain/
│   │   │   │   └── entities.py
│   │   │   ├── infrastructure/
│   │   │   │   ├── mappers.py
│   │   │   │   ├── models.py
│   │   │   │   └── repository.py
│   │   │   ├── presentation/
│   │   │   │   ├── dto.py
│   │   │   │   ├── mappers.py
│   │   │   │   └── routes.py
│   │   │   ├── di.py
│   │   │   └── enums.py
│   │   ├── courses/
│   │   ├── users/
│   │   │   ├── application/
│   │   │   │   ├── dto.py
│   │   │   │   └── service.py
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user.py
│   │   │   │   │   └── user_credential.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── enums.py
│   │   │   │   ├── exceptions.py
│   │   │   │   └── value_objects.py
│   │   │   ├── infrastructure/
│   │   │   │   ├── mappers/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user.py
│   │   │   │   │   └── user_credential.py
│   │   │   │   ├── models/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user_credential_model.py
│   │   │   │   │   └── user_model.py
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user_credential_repository.py
│   │   │   │   │   └── user_repository.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── password_hasher.py
│   │   │   ├── presentation/
│   │   │   │   ├── dto.py
│   │   │   │   ├── exception_handlers.py
│   │   │   │   ├── mappers.py
│   │   │   │   └── routes.py
│   │   │   ├── __init__.py
│   │   │   └── di.py
│   │   └── __init__.py
│   ├── shared/
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── di.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── di.py
│   │   ├── logger.py
│   │   ├── taskiq.py
│   │   └── uow.py
│   └── __init__.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── README.md
├── task.md
├── tz.md
└── uv.lock
