from pathlib import Path

import pytest
from pydantic import ValidationError

import tests.di
from shared.config import Settings
from tests.di import TestSettingsProvider

pytestmark = pytest.mark.unit


@pytest.fixture
def test_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for name in Settings.model_fields:
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.lower(), raising=False)
    values = {
        name: "5432" if field.annotation is int else "test-value" for name, field in Settings.model_fields.items()
    }
    values.update(DB_HOST="test-host", DB_USER="test-user", DB_NAME="postgres", DB_PASSWORD="example-test-secret")
    path = tmp_path / ".env.test"
    path.write_text("\n".join(f"{key}={value}" for key, value in values.items()), encoding="utf-8")
    monkeypatch.setattr(tests.di, "TEST_ENV_FILE", path)
    return path


def test_provider_loads_common_settings_from_test_file(test_env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(test_env.parent)
    (test_env.parent / ".env").write_text("DB_HOST=working-host\nDB_USER=working-user\n", encoding="utf-8")
    settings = TestSettingsProvider().settings()
    assert isinstance(settings, Settings)
    assert settings.DB_HOST == "test-host"
    assert settings.DB_USER == "test-user"
    assert settings.DB_PORT == 5432
    assert settings.DB_NAME == "postgres"


def test_provider_does_not_read_default_env_when_test_file_is_missing(test_env: Path) -> None:
    test_env.rename(test_env.parent / ".env")
    with pytest.raises(ValidationError) as caught:
        TestSettingsProvider().settings()
    assert {error["loc"][0] for error in caught.value.errors()} == set(Settings.model_fields)


def test_provider_preserves_standard_environment_priority(test_env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_HOST", "test-service-host")
    assert TestSettingsProvider().settings().DB_HOST == "test-service-host"
