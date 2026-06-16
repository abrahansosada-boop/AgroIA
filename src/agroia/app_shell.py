import hmac
from collections.abc import Sequence
from dataclasses import dataclass

import streamlit as st

from agroia.config import AppConfig, ConfigurationError, DataBackend, load_config
from agroia.data import load_base_datos, load_botiquin
from agroia.data_backend import DatabaseClient, create_database_client
from agroia.tenancy import TenantScopedDatabaseClient, UserContext, resolve_user_context
from agroia.ui.main_menu import render_main_menu


@dataclass
class AppContext:
    db: DatabaseClient
    raw_db: DatabaseClient
    data_backend: DataBackend
    user_context: UserContext
    botiquin: dict
    base_datos: dict
    es_administrador: bool
    opcion: str


def bootstrap_app(argv: Sequence[str] = ()) -> AppContext:
    configure_page()

    app_config = load_app_config(argv)
    require_login(app_config)

    st.title("🌾 Sistema de Inteligencia Agropecuaria v4.0")

    if app_config.data_backend is DataBackend.DEMO:
        st.warning(
            "Modo demo activo: estás usando datos locales temporales. "
            "Los cambios no se guardan en Supabase."
        )

    raw_db = create_database_client(app_config, st.session_state)
    user_context = resolve_user_context(raw_db, st.session_state)
    db = TenantScopedDatabaseClient(raw_db, user_context.tenant_id)
    render_tenant_badge(user_context)

    botiquin = load_botiquin()
    base_datos = load_base_datos(db)

    es_administrador = render_access_level(app_config, user_context)
    opcion = render_main_menu(user_context.role, es_administrador)

    return AppContext(
        db=db,
        raw_db=raw_db,
        data_backend=app_config.data_backend,
        user_context=user_context,
        botiquin=botiquin,
        base_datos=base_datos,
        es_administrador=es_administrador,
        opcion=opcion,
    )


def configure_page() -> None:
    st.set_page_config(
        page_title="AgroIA v4.0",
        page_icon="🐄",
        layout="wide",
    )


def load_app_config(argv: Sequence[str]) -> AppConfig:
    try:
        return load_config(secrets=st.secrets, argv=argv)
    except ConfigurationError as error:
        st.error(f"Configuración incompleta o inválida: {error}")
        st.stop()


def require_login(app_config: AppConfig) -> None:
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if st.session_state["autenticado"]:
        return

    st.title("🔒 Acceso Restringido - AgroIA")
    st.write("Por favor, identifícate para entrar al sistema del rancho.")

    _, col2, _ = st.columns([1, 2, 1])

    with col2:
        password = st.text_input("Contraseña Maestra:", type="password")

        if st.button("🚪 Entrar al Sistema", width="stretch"):
            if hmac.compare_digest(password, app_config.app_password):
                st.session_state["autenticado"] = True
                st.rerun()
            elif password != "":
                st.error("❌ Contraseña incorrecta.")

    st.stop()


def render_tenant_badge(user_context: UserContext) -> None:
    st.sidebar.caption(
        f"Espacio: {user_context.tenant_name} | Rol: {user_context.role.value}"
    )


def render_access_level(app_config: AppConfig, user_context: UserContext) -> bool:
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Nivel de Acceso")

    pin_secreto = st.sidebar.text_input("PIN de Seguridad:", type="password")
    pin_admin = hmac.compare_digest(pin_secreto, app_config.admin_pin)
    return user_context.can_manage_costs or pin_admin
