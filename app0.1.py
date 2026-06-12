import hmac
import streamlit as st
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.express as px
import pulp  
from supabase import create_client, Client
from modulos.panel_principal import renderizar_panel
from modulos.mortandad import renderizar_mortandad
from modulos.inventario import renderizar_inventario
from modulos.bascula import renderizar_bascula
from modulos.laboratorio import renderizar_laboratorio
from modulos.boveda import renderizar_boveda
from modulos.proyeccion import renderizar_proyeccion
from modulos.caja_negra import renderizar_caja_negra

from config import ConfigurationError, load_config


try:
    app_config = load_config(secrets=st.secrets)
except ConfigurationError as error:
    st.error(
        "Configuración incompleta o inválida. Define estas claves: "
        + ", ".join(error.invalid_keys)
    )
    st.stop()

@st.cache_resource
def init_connection(url, key):
    return create_client(url, key)

supabase = init_connection(app_config.supabase_url, app_config.supabase_key)

# (LOGIN)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔒 Acceso Restringido - AgroIA")
    st.write("Por favor, identifícate para entrar al sistema del rancho.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Contraseña Maestra:", type="password")
        if st.button("🚪 Entrar al Sistema", use_container_width=True):
            if hmac.compare_digest(password, app_config.app_password):
                st.session_state["autenticado"] = True
                st.rerun()
            elif password != "":
                st.error("❌ Contraseña incorrecta.")
    st.stop()
 
# CONFIGURACION
st.set_page_config(page_title="AgroIA v4.0", page_icon="🐄", layout="wide")
st.title("🌾 Sistema de Inteligencia Agropecuaria v4.0")

# CARGAR DATOS
try:
    with open("botiquin.json", "r", encoding="utf-8") as f:
        botiquin = json.load(f)
except FileNotFoundError:
    st.error("⚠️ Falta el archivo botiquin.json. El módulo veterinario no funcionará.")
    botiquin = {"desparasitantes": {}, "vacunas": {}}
def cargar_base_datos():
    try:

        with open("bd_agro_v2.json", "r") as archivo:
            base_fusionada = json.load(archivo)

        respuesta = supabase.table("inventario").select("*").execute()
        

        for fila in respuesta.data:
            insumo = fila["insumo"]
            if insumo in base_fusionada:
                base_fusionada[insumo]["stock_kg"] = float(fila["stock_kg"])
                base_fusionada[insumo]["costo_kg"] = float(fila["costo_kg"])
            
        return base_fusionada
        
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return {}
base_datos = cargar_base_datos()
# BITÁCORA EN LA NUBE
def registrar_bitacora(accion, detalle, gasto_total=0.0, kilos_procesados=0.0):
    """Guarda los movimientos en Supabase incluyendo dinero y volumen."""
    try:
        datos = {
            "accion": accion,
            "detalle": detalle,
            "gasto_total": float(gasto_total),
            "kilos_procesados": float(kilos_procesados)
        }
        supabase.table("bitacora").insert(datos).execute()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar en la bitácora: {e}")
        return False
        supabase.table("bitacora").insert(datos).execute()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar en la bitácora: {e}")
        return False

# MENÚ LATERAL
# SISTEMA DE ROLES (MODO ADMINISTRADOR VS OPERADOR)
st.sidebar.divider()
st.sidebar.subheader("🔐 Nivel de Acceso")
pin_secreto = st.sidebar.text_input("PIN de Seguridad:", type="password")

es_administrador = hmac.compare_digest(pin_secreto, app_config.admin_pin)

if es_administrador:
        st.sidebar.success("Modo Administrador Activado 🤠")
        modulos_disponibles = [
            "🏠 Panel Principal",
            "📦 Inventario de Insumos",
            "🧪 Super Laboratorio",
            "💰 Proyección Financiera",     
            "🕵️ Caja Negra (Bitácora)",     
            "💎 Bóveda Premium (IA)",
            "🪦 Gestión de Mortandad (Bajas)",
            "⚖️ Control de Peso (Báscula)"
        ]
else:
        st.sidebar.info("Modo Operador 👷")
        modulos_disponibles = [
            "🏠 Panel Principal",
            "📦 Inventario de Insumos",
            "🧪 Super Laboratorio",
            "🪦 Gestión de Mortandad (Bajas)",
            "⚖️ Control de Peso (Báscula)"
        ]

opcion = st.sidebar.radio("Seleccione un Módulo:", modulos_disponibles, key="modulo_actual")

# 🏠 PANEL PRINCIPAL (CENTRO DE MANDO)
if "Panel Principal" in opcion:
    renderizar_panel(supabase)

# INVENTARIO DE INSUMOS
elif "Inventario" in opcion:
    renderizar_inventario(base_datos, supabase, registrar_bitacora, es_administrador)

# SÚPER-LABORATORIO NUTRICIONAL Y FARMACOLÓGICO
elif "Laboratorio" in opcion:
    renderizar_laboratorio(base_datos, botiquin, supabase, registrar_bitacora, es_administrador)

# PROYECCIÓN FINANCIERA
elif "Proyección" in opcion:
    renderizar_proyeccion(registrar_bitacora)
    
# CAJA NEGRA
elif "Caja Negra" in opcion:
    renderizar_caja_negra(supabase)

# GESTIÓN DE MORTANDAD Y BAJAS
elif "Mortandad" in opcion:
    renderizar_mortandad(registrar_bitacora)

# CONTROL DE PESO (BÁSCULA)
elif "Peso" in opcion:
    renderizar_bascula(registrar_bitacora)

# 👑 MÓDULO: BÓVEDA PREMIUM DE GANADERÍA REGENERATIVA
elif "Bóveda" in opcion:
    renderizar_boveda(base_datos)