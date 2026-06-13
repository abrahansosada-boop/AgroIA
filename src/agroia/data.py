import json
from pathlib import Path

import streamlit as st
from supabase import create_client, Client


RESOURCE_DIR = Path(__file__).resolve().parents[2] / "resources"


@st.cache_resource
def init_connection(url: str, key: str) -> Client:
    return create_client(url, key)


def load_botiquin() -> dict:
    try:
        with (RESOURCE_DIR / "botiquin.json").open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ Falta el archivo botiquin.json. El módulo veterinario no funcionará.")
        return {"desparasitantes": {}, "vacunas": {}}


def load_base_datos(supabase: Client) -> dict:
    try:
        with (RESOURCE_DIR / "bd_agro_v2.json").open(encoding="utf-8") as archivo:
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


def registrar_bitacora(
    supabase: Client,
    accion: str,
    detalle: str,
    gasto_total: float = 0.0,
    kilos_procesados: float = 0.0,
) -> bool:
    try:
        datos = {
            "accion": accion,
            "detalle": detalle,
            "gasto_total": float(gasto_total),
            "kilos_procesados": float(kilos_procesados),
        }

        supabase.table("bitacora").insert(datos).execute()
        return True

    except Exception as e:
        st.error(f"⚠️ Error al guardar en la bitácora: {e}")
        return False