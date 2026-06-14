import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from urllib.parse import urlsplit, urlunsplit

BACKEND_ENVIRONMENT_KEY = "AGROIA_DATA_BACKEND"
COMMON_SECRET_KEYS = (
    "APP_PASSWORD",
    "ADMIN_PIN",
)
SUPABASE_SECRET_KEYS = (
    "SUPABASE_URL",
    "SUPABASE_KEY",
)


class ConfigurationError(Exception):
    def __init__(
        self,
        invalid_keys: tuple[str, ...],
        message: str | None = None,
    ) -> None:
        self.invalid_keys = invalid_keys
        super().__init__(
            message
            or f"Missing or invalid configuration keys: {', '.join(invalid_keys)}"
        )


class DataBackend(StrEnum):
    DEMO = "demo"
    SUPABASE = "supabase"


@dataclass(frozen=True)
class AppConfig:
    data_backend: DataBackend
    supabase_url: str | None
    supabase_key: str | None
    app_password: str
    admin_pin: str


def _read_secret(secrets: Mapping[str, Any], key: str) -> Any:
    try:
        return secrets[key]
    except (KeyError, FileNotFoundError):
        return None


def _normalize_supabase_url(value: str) -> str | None:
    candidate = value.strip()

    try:
        parsed = urlsplit(candidate)
        port = parsed.port
    except ValueError:
        return None

    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or (port is not None and not 0 < port < 65536)
        or parsed.path not in {"", "/"}
        or "?" in candidate
        or "#" in candidate
    ):
        return None

    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))


def _resolve_data_backend(
    environment: Mapping[str, Any],
    argv: Sequence[str],
) -> DataBackend:
    raw_backend = environment.get(BACKEND_ENVIRONMENT_KEY)
    cli_demo = "--demo" in argv

    if raw_backend is None:
        return DataBackend.DEMO if cli_demo else DataBackend.SUPABASE

    if not isinstance(raw_backend, str):
        raise ConfigurationError((BACKEND_ENVIRONMENT_KEY,))

    try:
        environment_backend = DataBackend(raw_backend.strip().lower())
    except ValueError as error:
        raise ConfigurationError((BACKEND_ENVIRONMENT_KEY,)) from error

    if cli_demo and environment_backend is DataBackend.SUPABASE:
        raise ConfigurationError(
            (BACKEND_ENVIRONMENT_KEY, "--demo"),
            "Conflicting data backend selectors: "
            "AGROIA_DATA_BACKEND=supabase cannot be combined with --demo",
        )

    return DataBackend.DEMO if cli_demo else environment_backend


def load_config(
    *,
    environ: Mapping[str, Any] | None = None,
    secrets: Mapping[str, Any] | None = None,
    argv: Sequence[str] = (),
) -> AppConfig:
    environment = os.environ if environ is None else environ
    secret_store = {} if secrets is None else secrets
    data_backend = _resolve_data_backend(environment, argv)
    values: dict[str, str] = {}
    invalid_keys: list[str] = []
    required_keys = COMMON_SECRET_KEYS
    if data_backend is DataBackend.SUPABASE:
        required_keys = SUPABASE_SECRET_KEYS + required_keys

    for key in required_keys:
        value = (
            environment[key]
            if key in environment
            else _read_secret(secret_store, key)
        )
        if not isinstance(value, str) or not value.strip():
            invalid_keys.append(key)
            continue

        if key == "SUPABASE_URL":
            normalized_url = _normalize_supabase_url(value)
            if normalized_url is None:
                invalid_keys.append(key)
                continue
            values[key] = normalized_url
            continue

        values[key] = value

    if invalid_keys:
        raise ConfigurationError(tuple(invalid_keys))

    return AppConfig(
        data_backend=data_backend,
        supabase_url=values.get("SUPABASE_URL"),
        supabase_key=values.get("SUPABASE_KEY"),
        app_password=values["APP_PASSWORD"],
        admin_pin=values["ADMIN_PIN"],
    )
