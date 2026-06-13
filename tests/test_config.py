import pytest

from agroia.config import ConfigurationError, load_config

VALID_ENVIRONMENT = {
    "SUPABASE_URL": "https://example.supabase.invalid",
    "SUPABASE_KEY": "fake-supabase-key",
    "APP_PASSWORD": "fake-app-password",
    "ADMIN_PIN": "0000",
}


class MissingSecretStore(dict[str, str]):
    def __getitem__(self, key: str) -> str:
        raise FileNotFoundError


def test_loads_configuration_from_environment() -> None:
    config = load_config(environ=VALID_ENVIRONMENT, secrets={})

    assert config.supabase_url == VALID_ENVIRONMENT["SUPABASE_URL"]
    assert config.supabase_key == VALID_ENVIRONMENT["SUPABASE_KEY"]
    assert config.app_password == VALID_ENVIRONMENT["APP_PASSWORD"]
    assert config.admin_pin == VALID_ENVIRONMENT["ADMIN_PIN"]


def test_loads_configuration_from_streamlit_secrets() -> None:
    config = load_config(environ={}, secrets=VALID_ENVIRONMENT)

    assert config.supabase_url == VALID_ENVIRONMENT["SUPABASE_URL"]
    assert config.supabase_key == VALID_ENVIRONMENT["SUPABASE_KEY"]
    assert config.app_password == VALID_ENVIRONMENT["APP_PASSWORD"]
    assert config.admin_pin == VALID_ENVIRONMENT["ADMIN_PIN"]


def test_normalizes_supabase_base_url() -> None:
    environment = {
        **VALID_ENVIRONMENT,
        "SUPABASE_URL": "  https://example.supabase.invalid/  ",
    }

    config = load_config(environ=environment, secrets={})

    assert config.supabase_url == "https://example.supabase.invalid"


@pytest.mark.parametrize(
    "invalid_url",
    [
        "https://example.supabase.invalid/rest/v1",
        "https://supabase.com/dashboard/project/example",
        "https://example.supabase.invalid/inventario",
        "https://example.supabase.invalid/?schema=public",
        "https://example.supabase.invalid/#settings",
    ],
)
def test_rejects_supabase_url_with_non_base_components(invalid_url: str) -> None:
    environment = {**VALID_ENVIRONMENT, "SUPABASE_URL": invalid_url}

    with pytest.raises(ConfigurationError) as error:
        load_config(environ=environment, secrets={})

    assert error.value.invalid_keys == ("SUPABASE_URL",)
    assert invalid_url not in str(error.value)


def test_environment_takes_precedence_per_key() -> None:
    environment = {"APP_PASSWORD": "environment-password"}
    config = load_config(environ=environment, secrets=VALID_ENVIRONMENT)

    assert config.app_password == "environment-password"
    assert config.admin_pin == VALID_ENVIRONMENT["ADMIN_PIN"]


@pytest.mark.parametrize("invalid_value", ["", "   ", 1234, None])
def test_rejects_empty_or_non_string_values(invalid_value: object) -> None:
    environment = {**VALID_ENVIRONMENT, "ADMIN_PIN": invalid_value}

    with pytest.raises(ConfigurationError) as error:
        load_config(environ=environment, secrets={})

    assert error.value.invalid_keys == ("ADMIN_PIN",)
    assert str(error.value) == "Missing or invalid configuration keys: ADMIN_PIN"


def test_reports_all_missing_keys_without_secret_values() -> None:
    with pytest.raises(ConfigurationError) as error:
        load_config(environ={}, secrets={})

    assert error.value.invalid_keys == (
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "APP_PASSWORD",
        "ADMIN_PIN",
    )
    assert "fake-supabase-key" not in str(error.value)


def test_handles_missing_streamlit_secrets_file() -> None:
    with pytest.raises(ConfigurationError) as error:
        load_config(environ={}, secrets=MissingSecretStore())

    assert error.value.invalid_keys == (
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "APP_PASSWORD",
        "ADMIN_PIN",
    )
