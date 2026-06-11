from collections.abc import Mapping
from dataclasses import dataclass
import os
from typing import Any


REQUIRED_SECRET_KEYS = (
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "APP_PASSWORD",
    "ADMIN_PIN",
)


class ConfigurationError(Exception):
    def __init__(self, invalid_keys: tuple[str, ...]) -> None:
        self.invalid_keys = invalid_keys
        super().__init__(
            f"Missing or invalid configuration keys: {', '.join(invalid_keys)}"
        )


@dataclass(frozen=True)
class AppConfig:
    supabase_url: str
    supabase_key: str
    app_password: str
    admin_pin: str


def _read_secret(secrets: Mapping[str, Any], key: str) -> Any:
    try:
        return secrets[key]
    except (KeyError, FileNotFoundError):
        return None


def load_config(
    *,
    environ: Mapping[str, Any] | None = None,
    secrets: Mapping[str, Any] | None = None,
) -> AppConfig:
    environment = os.environ if environ is None else environ
    secret_store = {} if secrets is None else secrets
    values: dict[str, str] = {}
    invalid_keys: list[str] = []

    for key in REQUIRED_SECRET_KEYS:
        value = environment[key] if key in environment else _read_secret(secret_store, key)
        if not isinstance(value, str) or not value.strip():
            invalid_keys.append(key)
            continue
        values[key] = value

    if invalid_keys:
        raise ConfigurationError(tuple(invalid_keys))

    return AppConfig(
        supabase_url=values["SUPABASE_URL"],
        supabase_key=values["SUPABASE_KEY"],
        app_password=values["APP_PASSWORD"],
        admin_pin=values["ADMIN_PIN"],
    )
