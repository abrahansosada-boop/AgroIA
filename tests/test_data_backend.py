from agroia.config import AppConfig, DataBackend
from agroia.data_backend import create_database_client
from agroia.demo_supabase import DemoSupabaseClient


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


def test_demo_client_persists_within_session(monkeypatch) -> None:
    session_state = {}
    supabase_calls = []
    monkeypatch.setattr(
        "agroia.data_backend.init_supabase_connection",
        lambda url, key: supabase_calls.append((url, key)),
    )

    first = create_database_client(
        make_config(DataBackend.DEMO),
        session_state,
    )
    second = create_database_client(
        make_config(DataBackend.DEMO),
        session_state,
    )

    assert isinstance(first, DemoSupabaseClient)
    assert second is first
    assert supabase_calls == []


def test_demo_clients_are_isolated_between_sessions() -> None:
    first = create_database_client(make_config(DataBackend.DEMO), {})
    second = create_database_client(make_config(DataBackend.DEMO), {})

    assert first is not second


def test_supabase_backend_uses_real_client_factory(monkeypatch) -> None:
    expected_client = object()
    calls = []
    monkeypatch.setattr(
        "agroia.data_backend.init_supabase_connection",
        lambda url, key: calls.append((url, key)) or expected_client,
    )

    client = create_database_client(
        make_config(DataBackend.SUPABASE),
        {},
    )

    assert client is expected_client
    assert calls == [
        ("https://example.supabase.invalid", "fake-supabase-key")
    ]
