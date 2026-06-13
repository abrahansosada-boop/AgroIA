from dataclasses import dataclass, field

import pytest

from agroia.ui import main_menu


@dataclass
class FakeSidebar:
    session_state: dict[str, str]
    messages: list[tuple[str, str]] = field(default_factory=list)
    radio_options: tuple[str, ...] = ()

    def success(self, message: str) -> None:
        self.messages.append(("success", message))

    def info(self, message: str) -> None:
        self.messages.append(("info", message))

    def radio(
        self,
        _label: str,
        options: tuple[str, ...],
        *,
        key: str,
    ) -> str:
        self.radio_options = options
        return self.session_state[key]


class FakeStreamlit:
    def __init__(self, session_state: dict[str, str] | None = None) -> None:
        self.session_state = session_state or {}
        self.sidebar = FakeSidebar(self.session_state)


def render_menu(
    monkeypatch: pytest.MonkeyPatch,
    *,
    es_administrador: bool,
    selected: str | None = None,
) -> tuple[str, FakeStreamlit]:
    session_state = {}
    if selected is not None:
        session_state[main_menu.MODULE_STATE_KEY] = selected

    fake_streamlit = FakeStreamlit(session_state)
    monkeypatch.setattr(main_menu, "st", fake_streamlit)

    option = main_menu.render_main_menu(es_administrador)
    return option, fake_streamlit


def test_initializes_panel_principal_as_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    option, fake_streamlit = render_menu(
        monkeypatch,
        es_administrador=False,
    )

    assert option == main_menu.DEFAULT_MODULE
    assert (
        fake_streamlit.session_state[main_menu.MODULE_STATE_KEY]
        == main_menu.DEFAULT_MODULE
    )


@pytest.mark.parametrize(
    ("es_administrador", "expected_modules", "expected_message"),
    [
        (
            False,
            main_menu.OPERATOR_MODULES,
            ("info", "Modo Operador 👷"),
        ),
        (
            True,
            main_menu.ADMIN_MODULES,
            ("success", "Modo Administrador Activado 🤠"),
        ),
    ],
)
def test_renders_modules_for_access_level(
    monkeypatch: pytest.MonkeyPatch,
    es_administrador: bool,
    expected_modules: tuple[str, ...],
    expected_message: tuple[str, str],
) -> None:
    _, fake_streamlit = render_menu(
        monkeypatch,
        es_administrador=es_administrador,
    )

    assert fake_streamlit.sidebar.radio_options == expected_modules
    assert fake_streamlit.sidebar.messages == [expected_message]


@pytest.mark.parametrize(
    "selected",
    [
        main_menu.LABORATORY_MODULE,
        main_menu.INVENTORY_MODULE,
    ],
)
def test_preserves_quick_navigation_selection(
    monkeypatch: pytest.MonkeyPatch,
    selected: str,
) -> None:
    option, fake_streamlit = render_menu(
        monkeypatch,
        es_administrador=False,
        selected=selected,
    )

    assert option == selected
    assert fake_streamlit.session_state[main_menu.MODULE_STATE_KEY] == selected


def test_normalizes_accented_laboratory_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    option, fake_streamlit = render_menu(
        monkeypatch,
        es_administrador=False,
        selected="🧪 Súper Laboratorio",
    )

    assert option == main_menu.LABORATORY_MODULE
    assert (
        fake_streamlit.session_state[main_menu.MODULE_STATE_KEY]
        == main_menu.LABORATORY_MODULE
    )


def test_resets_unavailable_module_to_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    option, fake_streamlit = render_menu(
        monkeypatch,
        es_administrador=False,
        selected="💰 Proyección Financiera",
    )

    assert option == main_menu.DEFAULT_MODULE
    assert (
        fake_streamlit.session_state[main_menu.MODULE_STATE_KEY]
        == main_menu.DEFAULT_MODULE
    )
