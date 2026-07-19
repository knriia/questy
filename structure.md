questy/
├── di/
│   └── container.py
├── src/
│   ├── apps/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── scheduler.py
│   │   └── worker.py
│   ├── core/
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── di.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── di.py
│   │   ├── logger.py
│   │   └── taskiq.py
│   ├── integrations/
│   │   └── telegram/
│   │       ├── di.py
│   │       └── sender.py
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
│   │   │   └── di.py
│   │   └── __init__.py
│   └── __init__.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── README.md
└── requirements.txt
