from types import SimpleNamespace

import pytest

from agroia.ui import router

PAGE_RENDERERS = (
    "render_dashboard_page",
    "render_inventory_page",
    "render_laboratory_page",
    "render_financial_projection_page",
    "render_black_box_page",
    "render_mortality_page",
    "render_weight_page",
    "render_resilience_vault_page",
)


def install_renderer_spies(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[str, object]]:
    calls = []

    for renderer_name in PAGE_RENDERERS:
        def record_call(ctx, name=renderer_name):
            calls.append((name, ctx))

        monkeypatch.setattr(router, renderer_name, record_call)

    return calls


@pytest.mark.parametrize(
    ("option", "expected_renderer"),
    [
        ("🏠 Panel Principal", "render_dashboard_page"),
        ("📦 Inventario de Insumos", "render_inventory_page"),
        ("🧪 Super Laboratorio", "render_laboratory_page"),
        ("Perfil Genético", "render_laboratory_page"),
        ("Motor IA", "render_laboratory_page"),
        ("💰 Proyección Financiera", "render_financial_projection_page"),
        ("🕵️ Caja Negra (Bitácora)", "render_black_box_page"),
        ("🪦 Gestión de Mortandad (Bajas)", "render_mortality_page"),
        ("⚖️ Control de Peso (Báscula)", "render_weight_page"),
        ("💎 Bóveda Premium (IA)", "render_resilience_vault_page"),
    ],
)
def test_dispatches_selected_page(
    monkeypatch: pytest.MonkeyPatch,
    option: str,
    expected_renderer: str,
) -> None:
    calls = install_renderer_spies(monkeypatch)
    ctx = SimpleNamespace(opcion=option)

    router.render_selected_page(ctx)

    assert calls == [(expected_renderer, ctx)]


def test_unknown_option_renders_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_renderer_spies(monkeypatch)
    ctx = SimpleNamespace(opcion="Módulo desconocido")

    router.render_selected_page(ctx)

    assert calls == []
