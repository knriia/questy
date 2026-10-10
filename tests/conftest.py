import pytest

from tests.fakes.uow import FakeUoW


@pytest.fixture
def uow() -> FakeUoW:
    return FakeUoW()
