from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from modules.activity.application.services.activity import ActivityService
from modules.activity.domain.entities.activity import ActivityEntity, SavedActivityEntity
from modules.activity.enums import ActivityStatus, ActivityType
from modules.activity.presentation.dto.activity import ActivityCreateDTO
from modules.activity.presentation.mappers.activity import activity_dto_to_entity, activity_entity_to_dto
from modules.activity.presentation.routes.activity import activity_router
from modules.auth.application.dto import UserAuthCredentialCommand
from modules.auth.application.service import AuthService
from modules.auth.presentation.exception_handlers import setup_auth_exception_handlers
from shared.config import Settings
from tests.fakes.auth_login import AuthLoginContext, add_login_user, create_auth_login_context
from tests.fakes.uow import FakeUoW
from tests.support.asgi import post_json

pytestmark = pytest.mark.integration_no_db

TEST_USER_ID = UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba812")


class ActivityRepositoryFake:
    async def create_activity(self, activity: ActivityEntity) -> SavedActivityEntity:
        now = datetime.now(UTC)
        return SavedActivityEntity(
            id=activity.id,
            user_id=activity.user_id,
            title=activity.title,
            description=activity.description,
            activity_type=activity.activity_type,
            status=activity.status,
            fields_schema=activity.fields_schema,
            created_at=now,
            updated_at=now,
        )


class ActivityProviderForTest(Provider):
    def __init__(self, context: AuthLoginContext, activity_service: ActivityService) -> None:
        super().__init__()
        self.context = context
        self.activity_service = activity_service

    @provide(scope=Scope.REQUEST)
    def provide_activity_service(self) -> ActivityService:
        return self.activity_service

    @provide(scope=Scope.REQUEST)
    def auth_service(self) -> AuthService:
        return self.context.service

    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return self.context.settings


@pytest_asyncio.fixture
async def activity_app() -> AsyncIterator[tuple[FastAPI, FakeUoW, AuthLoginContext]]:
    uow = FakeUoW()
    service = ActivityService(repository=ActivityRepositoryFake(), uow=uow)
    context = create_auth_login_context()
    app = FastAPI()
    app.include_router(activity_router)
    setup_auth_exception_handlers(app)
    container = make_async_container(ActivityProviderForTest(context=context, activity_service=service))
    setup_dishka(container, app)
    try:
        yield app, uow, context
    finally:
        await container.close()


def test_activity_dto_mapper_uses_principal_user_id_and_defaults() -> None:
    dto = ActivityCreateDTO(
        title="Reading",
        activity_type=ActivityType.LEARNING,
        fields_schema={"fields": []},
    )

    entity = activity_dto_to_entity(activity_dto=dto, user_id=TEST_USER_ID)

    assert isinstance(entity, ActivityEntity)
    assert entity.user_id == TEST_USER_ID
    assert entity.title == dto.title
    assert entity.description is None
    assert entity.activity_type is ActivityType.LEARNING
    assert entity.status is ActivityStatus.ACTIVE
    assert entity.fields_schema == dto.fields_schema


def test_activity_entity_to_dto_copies_saved_activity_fields() -> None:
    now = datetime.now(UTC)
    entity = SavedActivityEntity(
        id=UUID("0194f8b4-2b9a-7d65-a6df-9d4ebd8ba814"),
        user_id=TEST_USER_ID,
        title="Reading",
        description="Daily reading",
        activity_type=ActivityType.LEARNING,
        status=ActivityStatus.ACTIVE,
        fields_schema={"fields": []},
        created_at=now,
        updated_at=now,
    )

    dto = activity_entity_to_dto(activity_entity=entity)

    assert dto.id == entity.id
    assert dto.user_id == TEST_USER_ID
    assert dto.title == entity.title
    assert dto.description == entity.description
    assert dto.activity_type is ActivityType.LEARNING
    assert dto.status is ActivityStatus.ACTIVE
    assert dto.fields_schema == entity.fields_schema
    assert dto.created_at == now
    assert dto.updated_at == now


@pytest.mark.asyncio
async def test_create_activity_endpoint_uses_principal_and_returns_saved_activity(
    activity_app: tuple[FastAPI, FakeUoW, AuthLoginContext],
) -> None:
    app, uow, context = activity_app
    user = add_login_user(context)
    context.hasher.results["stored-password-hash"] = True
    login = await context.service.auth_user(
        UserAuthCredentialCommand(
            identifier=user.username.value,
            password="correct password",
            ip_address="192.0.2.1",
            user_agent="pytest-agent",
            client_name="pytest",
        )
    )

    status, body = await post_json(
        app,
        "/activities/create",
        {
            "title": "Reading",
            "description": "Daily reading",
            "activity_type": "learning",
            "fields_schema": {"fields": []},
        },
        request_headers=[(b"authorization", f"Bearer {login.access_token}".encode())],
    )

    assert status == 200
    assert body["user_id"] == str(user.id)
    assert body["title"] == "Reading"
    assert body["description"] == "Daily reading"
    assert body["activity_type"] == "learning"
    assert body["status"] == "active"
    assert body["fields_schema"] == {"fields": []}
    assert body["created_at"]
    assert body["updated_at"]
    assert uow.commit_count == 1
    assert uow.rollback_count == 1


@pytest.mark.asyncio
async def test_create_activity_endpoint_requires_authentication(
    activity_app: tuple[FastAPI, FakeUoW, AuthLoginContext],
) -> None:
    app, uow, _ = activity_app

    status, body = await post_json(
        app,
        "/activities/create",
        {
            "title": "Reading",
            "activity_type": "learning",
            "fields_schema": {"fields": []},
        },
    )

    assert status == 401
    assert body["detail"]["code"] == "user_not_authenticated"
    assert uow.commit_count == 0
