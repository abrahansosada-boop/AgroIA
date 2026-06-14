from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agroia import app_shell
from agroia.config import AppConfig, DataBackend


def make_config(backend: DataBackend) -> AppConfig:
    return AppConfig(
        data_backend=backend,
        supabase_url=(
            "https://example.supabase.invalid"
            if backend is DataBackend.SUPABASE
            else None
        ),
        supabase_key=(
            "fake-supabase-key" if backend is DataBackend.SUPABASE else None
        ),
        app_password="fake-app-password",
        admin_pin="0000",
    )


@pytest.mark.parametrize(
    ("backend", "warning_count"),
    [
        (DataBackend.DEMO, 1),
        (DataBackend.SUPABASE, 0),
    ],
)
def test_bootstrap_selects_database_and_renders_demo_warning(
    monkeypatch,
    backend: DataBackend,
    warning_count: int,
) -> None:
    config = make_config(backend)
    db = object()
    session_state = {}
    st = SimpleNamespace(
        session_state=session_state,
        title=MagicMock(),
        warning=MagicMock(),
    )

    monkeypatch.setattr(app_shell, "st", st)
    monkeypatch.setattr(app_shell, "configure_page", MagicMock())
    monkeypatch.setattr(app_shell, "load_app_config", lambda argv: config)
    monkeypatch.setattr(app_shell, "require_login", MagicMock())
    create_client = MagicMock(return_value=db)
    monkeypatch.setattr(app_shell, "create_database_client", create_client)
    monkeypatch.setattr(app_shell, "load_botiquin", lambda: {"vacunas": {}})
    load_base_datos = MagicMock(return_value={"maiz_molido": {}})
    monkeypatch.setattr(app_shell, "load_base_datos", load_base_datos)
    monkeypatch.setattr(app_shell, "render_access_level", lambda _: True)
    monkeypatch.setattr(
        app_shell,
        "render_main_menu",
        lambda _: "🏠 Panel Principal",
    )

    ctx = app_shell.bootstrap_app(("--demo",))

    create_client.assert_called_once_with(config, session_state)
    load_base_datos.assert_called_once_with(db)
    assert st.warning.call_count == warning_count
    assert ctx.db is db
    assert ctx.data_backend is backend
