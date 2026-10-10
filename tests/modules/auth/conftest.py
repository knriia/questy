import pytest

from modules.auth.application.dto import UserRegisterCommand
from tests.fakes.registration import RegistrationContext, create_registration_context


@pytest.fixture
def registration() -> RegistrationContext:
    return create_registration_context()


@pytest.fixture
def register_command() -> UserRegisterCommand:
    return UserRegisterCommand(
        username="knriia", email="knriia@example.com", timezone="Asia/Tomsk", password="valid password phrase"
    )
