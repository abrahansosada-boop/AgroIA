import hmac
from dataclasses import dataclass

import streamlit as st
from supabase import Client

from agroia.config import ConfigurationError, load_config
from agroia.data import (
    init_connection,
    load_base_datos,
    load_botiquin,
)
from agroia.ui.main_menu import render_main_menu


@dataclass
class AppContext:
    supabase: Client
    botiquin: dict
    base_datos: dict
    es_administrador: bool
    opcion: str


def bootstrap_app() -> AppContext:
    configure_page()

    app_config = load_app_config()
    require_login(app_config)

    st.title("🌾 Sistema de Inteligencia Agropecuaria v4.0")

    supabase = init_connection(
        app_config.supabase_url,
        app_config.supabase_key,
    )

    botiquin = load_botiquin()
    base_datos = load_base_datos(supabase)

    es_administrador = render_access_level(app_config)
    opcion = render_main_menu(es_administrador)

    return AppContext(
        supabase=supabase,
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


def load_app_config():
    try:
        return load_config(secrets=st.secrets)
    except ConfigurationError as error:
        st.error(
            "Configuración incompleta o inválida. Define estas claves: "
            + ", ".join(error.invalid_keys)
        )
        st.stop()


def require_login(app_config) -> None:
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if st.session_state["autenticado"]:
        return

    st.title("🔒 Acceso Restringido - AgroIA")
    st.write("Por favor, identifícate para entrar al sistema del rancho.")

    _, col2, _ = st.columns([1, 2, 1])

    with col2:
        password = st.text_input("Contraseña Maestra:", type="password")

        if st.button("🚪 Entrar al Sistema", use_container_width=True):
            if hmac.compare_digest(password, app_config.app_password):
                st.session_state["autenticado"] = True
                st.rerun()
            elif password != "":
                st.error("❌ Contraseña incorrecta.")

    st.stop()


def render_access_level(app_config) -> bool:
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Nivel de Acceso")

    pin_secreto = st.sidebar.text_input("PIN de Seguridad:", type="password")
    return hmac.compare_digest(pin_secreto, app_config.admin_pin)
