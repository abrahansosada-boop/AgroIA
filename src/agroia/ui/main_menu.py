import streamlit as st

DEFAULT_MODULE = "🏠 Panel Principal"
LABORATORY_MODULE = "🧪 Super Laboratorio"
INVENTORY_MODULE = "📦 Inventario de Insumos"
MODULE_STATE_KEY = "modulo_actual"

OPERATOR_MODULES = (
    DEFAULT_MODULE,
    INVENTORY_MODULE,
    LABORATORY_MODULE,
    "🪦 Gestión de Mortandad (Bajas)",
    "⚖️ Control de Peso (Báscula)",
)

ADMIN_MODULES = (
    DEFAULT_MODULE,
    INVENTORY_MODULE,
    LABORATORY_MODULE,
    "💰 Proyección Financiera",
    "🕵️ Caja Negra (Bitácora)",
    "💎 Bóveda Premium (IA)",
    "🪦 Gestión de Mortandad (Bajas)",
    "⚖️ Control de Peso (Báscula)",
)


def render_main_menu(es_administrador: bool) -> str:
    if es_administrador:
        st.sidebar.success("Modo Administrador Activado 🤠")
        modulos_disponibles = ADMIN_MODULES
    else:
        st.sidebar.info("Modo Operador 👷")
        modulos_disponibles = OPERATOR_MODULES

    modulo_actual = st.session_state.get(MODULE_STATE_KEY, DEFAULT_MODULE)
    if modulo_actual == "🧪 Súper Laboratorio":
        modulo_actual = LABORATORY_MODULE

    if modulo_actual not in modulos_disponibles:
        modulo_actual = DEFAULT_MODULE

    st.session_state[MODULE_STATE_KEY] = modulo_actual

    opcion = st.sidebar.radio(
        "Seleccione un Módulo:",
        modulos_disponibles,
        key=MODULE_STATE_KEY,
    )

    return str(opcion)
