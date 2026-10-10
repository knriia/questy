import pytest

from modules.user.application.service import UserService
from tests.fakes.uow import FakeUoW
from tests.fakes.user_repository import InMemoryUserRepository


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def service(user_repo: InMemoryUserRepository, uow: FakeUoW) -> UserService:
    return UserService(user_repo=user_repo, uow=uow)
