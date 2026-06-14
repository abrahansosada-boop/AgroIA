import pytest

from agroia.config import ConfigurationError, DataBackend, load_config

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

    assert config.data_backend is DataBackend.SUPABASE
    assert config.supabase_url == VALID_ENVIRONMENT["SUPABASE_URL"]
    assert config.supabase_key == VALID_ENVIRONMENT["SUPABASE_KEY"]
    assert config.app_password == VALID_ENVIRONMENT["APP_PASSWORD"]
    assert config.admin_pin == VALID_ENVIRONMENT["ADMIN_PIN"]


def test_loads_configuration_from_streamlit_secrets() -> None:
    config = load_config(environ={}, secrets=VALID_ENVIRONMENT)

    assert config.data_backend is DataBackend.SUPABASE
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


@pytest.mark.parametrize(
    ("environment", "argv"),
    [
        ({"AGROIA_DATA_BACKEND": "demo"}, ()),
        ({}, ("--demo",)),
        ({"AGROIA_DATA_BACKEND": "demo"}, ("--demo",)),
    ],
)
def test_demo_mode_does_not_require_supabase_credentials(
    environment: dict[str, str],
    argv: tuple[str, ...],
) -> None:
    config = load_config(
        environ={
            **environment,
            "APP_PASSWORD": "fake-app-password",
            "ADMIN_PIN": "0000",
        },
        secrets={},
        argv=argv,
    )

    assert config.data_backend is DataBackend.DEMO
    assert config.supabase_url is None
    assert config.supabase_key is None


def test_explicit_supabase_backend_uses_supabase() -> None:
    config = load_config(
        environ={
            **VALID_ENVIRONMENT,
            "AGROIA_DATA_BACKEND": "supabase",
        },
        secrets={},
    )

    assert config.data_backend is DataBackend.SUPABASE


def test_demo_mode_still_requires_login_configuration() -> None:
    with pytest.raises(ConfigurationError) as error:
        load_config(
            environ={"AGROIA_DATA_BACKEND": "demo"},
            secrets={},
        )

    assert error.value.invalid_keys == ("APP_PASSWORD", "ADMIN_PIN")


def test_rejects_invalid_backend_value() -> None:
    with pytest.raises(ConfigurationError) as error:
        load_config(
            environ={
                **VALID_ENVIRONMENT,
                "AGROIA_DATA_BACKEND": "sqlite",
            },
            secrets={},
        )

    assert error.value.invalid_keys == ("AGROIA_DATA_BACKEND",)


def test_rejects_conflicting_explicit_backend_selectors() -> None:
    with pytest.raises(ConfigurationError) as error:
        load_config(
            environ={
                **VALID_ENVIRONMENT,
                "AGROIA_DATA_BACKEND": "supabase",
            },
            secrets={},
            argv=("--demo",),
        )

    assert error.value.invalid_keys == ("AGROIA_DATA_BACKEND", "--demo")
    assert "cannot be combined" in str(error.value)
