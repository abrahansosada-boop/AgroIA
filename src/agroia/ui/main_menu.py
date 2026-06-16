import streamlit as st

from agroia.tenancy import Role

DEFAULT_MODULE = "Panel Principal"
LABORATORY_MODULE = "Super Laboratorio"
INVENTORY_MODULE = "Inventario de Insumos"
MODULE_STATE_KEY = "modulo_actual"

OPERATOR_MODULES = (
    DEFAULT_MODULE,
    INVENTORY_MODULE,
    LABORATORY_MODULE,
    "Gestion de Mortandad (Bajas)",
    "Control de Peso (Bascula)",
)

ADVISOR_MODULES = (
    DEFAULT_MODULE,
    INVENTORY_MODULE,
    LABORATORY_MODULE,
    "Proyeccion Financiera",
    "Gestion de Mortandad (Bajas)",
    "Control de Peso (Bascula)",
)

ADMIN_MODULES = (
    DEFAULT_MODULE,
    INVENTORY_MODULE,
    LABORATORY_MODULE,
    "Proyeccion Financiera",
    "Caja Negra (Bitacora)",
    "Boveda Premium (IA)",
    "Gestion de Mortandad (Bajas)",
    "Control de Peso (Bascula)",
)


def render_main_menu(role: Role | bool, es_administrador: bool | None = None) -> str:
    if isinstance(role, bool):
        es_administrador = role
        role = Role.ADMIN if role else Role.OPERATOR
    elif es_administrador is None:
        es_administrador = role in {Role.OWNER, Role.ADMIN}

    if role in {Role.OWNER, Role.ADMIN} or es_administrador:
        st.sidebar.success("Modo Administrador Activado")
        modulos_disponibles = ADMIN_MODULES
    elif role is Role.ADVISOR:
        st.sidebar.info("Modo Asesor")
        modulos_disponibles = ADVISOR_MODULES
    else:
        st.sidebar.info("Modo Operador")
        modulos_disponibles = OPERATOR_MODULES

    modulo_actual = st.session_state.get(MODULE_STATE_KEY, DEFAULT_MODULE)
    if modulo_actual in {"Super Laboratorio", "Súper Laboratorio"}:
        modulo_actual = LABORATORY_MODULE

    if modulo_actual not in modulos_disponibles:
        modulo_actual = DEFAULT_MODULE

    st.session_state[MODULE_STATE_KEY] = modulo_actual

    opcion = st.sidebar.radio(
        "Seleccione un Modulo:",
        modulos_disponibles,
        key=MODULE_STATE_KEY,
    )

    return str(opcion)
