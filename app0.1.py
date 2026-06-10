import streamlit as st
import json
import pandas as pd
import yfinance as yf
import os
from datetime import datetime
import plotly.express as px
import pulp  
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

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
            if password == "rancho2026":  
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

es_administrador = (pin_secreto == "2026")

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
    st.title("🚜 AgroIA: Centro de Mando")
    st.markdown("Bienvenido al resumen operativo en tiempo real del rancho.")
    
    gasto_real = 0.0
    lotes_reales = 0
    costo_promedio = 0.0
    
    try:

        respuesta_b = supabase.table("bitacora").select("gasto_total, kilos_procesados").execute()
        if respuesta_b.data:
            df_finanzas = pd.DataFrame(respuesta_b.data)
            
            gasto_real = df_finanzas['gasto_total'].sum()
            
            lotes_reales = len(df_finanzas[df_finanzas['gasto_total'] > 0])
            
            kilos_totales = df_finanzas['kilos_procesados'].sum()
            if kilos_totales > 0:
                costo_promedio = gasto_real / kilos_totales
                
    except Exception as e:
        st.error(f"⚠️ Radar financiero desconectado: {e}")

    st.subheader("📈 Resumen de Operación (Mensual)")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    kpi1.metric(label="💰 Gasto Total Acumulado", value=f"${gasto_real:,.2f} MXN")
    kpi2.metric(label="🔄 Lotes / Movimientos", value=f"{lotes_reales} Registros")
    kpi3.metric(label="📉 Costo Promedio Histórico", value=f"${costo_promedio:,.2f} / Kg")
    
    st.divider()
    st.subheader("⚡ Acciones Rápidas")

    def saltar_a_lab():
        st.session_state["modulo_actual"] = "🧪 Super Laboratorio"

    def saltar_a_inv():
        st.session_state["modulo_actual"] = "📦 Inventario de Insumos"

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        st.info("⚖️ Calcula y optimiza tu revoltura (Manual o IA).")
        st.button("Ir al Súper-Laboratorio", use_container_width=True, on_click=saltar_a_lab)

    with col_btn2:
        st.success("📦 Revisa y actualiza tus existencias.")
        st.button("Ir a Inventario de Insumos", use_container_width=True, on_click=saltar_a_inv)

# INVENTARIO DE INSUMOS
elif "Inventario" in opcion:
    st.header("📦 Control de Bodega y Precios")
    
    st.subheader("📊 Estado Actual del Inventario")
    
    # LÓGICA DE ALERTAS HÍBRIDAS 
    col_alerta1, col_alerta2 = st.columns(2)
    with col_alerta1:
        tipo_alerta = st.radio("Configuración de Alertas:", ["⚖️ Por Kilos Mínimos", "⏳ Por Días Restantes"], horizontal=True)
    with col_alerta2:
        if "Días" in tipo_alerta:
            consumo_diario = st.number_input("Consumo estimado del rancho (kg/día)", min_value=1.0, value=300.0, step=50.0)
            limite_critico = st.number_input("Alerta Roja a los (Días):", min_value=1, value=3, step=1)
        else:
            limite_critico = st.number_input("Alerta Roja a los (Kilos):", min_value=1.0, value=500.0, step=100.0)

    inventario_visual = []
    for insumo, datos in base_datos.items():
        stock = datos.get("stock_kg", 0)
        precio = datos.get("costo_kg", 0)
        
        # Evaluador Inteligente de Alertas
        if "Días" in tipo_alerta:
            dias_restantes = stock / consumo_diario if consumo_diario > 0 else 0
            if dias_restantes <= limite_critico:
                estatus = f"🔴 CRÍTICO ({dias_restantes:.1f} días)"
            elif dias_restantes <= limite_critico + 4:
                estatus = f"🟡 PRECAUCIÓN ({dias_restantes:.1f} días)"
            else:
                estatus = f"🟢 ÓPTIMO ({dias_restantes:.1f} días)"
        else:
            if stock <= limite_critico:
                estatus = "🔴 CRÍTICO"
            elif stock <= limite_critico * 2:
                estatus = "🟡 PRECAUCIÓN"
            else:
                estatus = "🟢 ÓPTIMO"
                
        inventario_visual.append({
            "Insumo": insumo.upper(),
            "Stock en Bodega (kg)": round(stock, 2),
            "Costo Actual ($/kg)": round(precio, 2),
            "Estado": estatus
        })
        
    df_inventario = pd.DataFrame(inventario_visual)
    if not es_administrador:
        df_inventario = df_inventario.drop(columns=["Costo Actual ($/kg)"])        
    st.dataframe(df_inventario, use_container_width=True, hide_index=True)
    
    # ACTUALIZAR INVENTARIO, PRECIOS O MERMAS
    st.divider()
    st.subheader("🛠️ Auditoría y Movimientos de Bodega")
    
    col_ed1, col_ed2 = st.columns(2)
    with col_ed1:
        insumo_edit = st.selectbox("Seleccione Insumo:", list(base_datos.keys()))
        tipo_movimiento = st.radio("Tipo de Movimiento:", [
            "📦 Ingreso / Compra (Suma)", 
            "⚖️ Ajuste de Inventario (Suma/Resta)", 
            "🐀 Reportar Merma (Resta y Fuga de Dinero)"
        ])
        
    with col_ed2:
        kilos_mov = st.number_input("Kilos del movimiento", min_value=0.0, value=0.0, step=50.0)
        
        if "Ingreso" in tipo_movimiento:
            nuevo_precio = st.number_input("Nuevo precio de compra ($/kg)", value=float(base_datos[insumo_edit]["costo_kg"]), step=0.1)
        elif "Merma" in tipo_movimiento:
            causa_merma = st.selectbox("Causa de la pérdida:", ["Humedad/Lluvia", "Plagas (Ratones/Gorgojo)", "Accidente/Rotura", "Robo/Extravío"])
            perdida_calculada = kilos_mov * base_datos[insumo_edit]['costo_kg']
            st.warning(f"💸 Esto generará una pérdida auditada de **${perdida_calculada:,.2f} MXN**")

    if st.button("💾 Registrar Movimiento en Bóveda", use_container_width=True):
        if kilos_mov <= 0 and "Ajuste" not in tipo_movimiento:
             st.error("⚠️ Tienes que poner más de 0 kilos para hacer este movimiento.")
        else:
            try:
                stock_actual = base_datos[insumo_edit]["stock_kg"]
                precio_actual = base_datos[insumo_edit]["costo_kg"]
                
                if "Ingreso" in tipo_movimiento:
                    nuevo_stock = stock_actual + kilos_mov
                    precio_final = nuevo_precio
                    tipo_accion = "Compra de Insumo"
                    detalle = f"Ingreso de {kilos_mov}kg de {insumo_edit.upper()}. Nuevo precio: ${precio_final}"
                    
                elif "Ajuste" in tipo_movimiento:
                    nuevo_stock = stock_actual + kilos_mov 
                    precio_final = precio_actual
                    tipo_accion = "Ajuste de Bodega"
                    detalle = f"Ajuste manual de {insumo_edit.upper()}: {kilos_mov}kg."
                    
                elif "Merma" in tipo_movimiento:
                    nuevo_stock = stock_actual - kilos_mov
                    precio_final = precio_actual
                    perdida_dinero = kilos_mov * precio_actual
                    tipo_accion = "Merma Financiera"
                    detalle = f"MERMA de {kilos_mov}kg de {insumo_edit.upper()} por {causa_merma}. Fuga: ${perdida_dinero:,.2f}"

                respuesta = supabase.table("inventario").update({
                    "stock_kg": float(nuevo_stock),
                    "costo_kg": float(precio_final)
                }).eq("insumo", insumo_edit).execute()

                base_datos[insumo_edit]["stock_kg"] = float(nuevo_stock)
                base_datos[insumo_edit]["costo_kg"] = float(precio_final)
                
                registrar_bitacora(tipo_accion, detalle)
                st.success(f"✅ ¡Movimiento de {insumo_edit.upper()} registrado exitosamente!")
                
                import time
                time.sleep(1) 
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error al conectar con la bóveda en la nube: {e}")

    st.divider()
    st.subheader("🌐 Radar Satelital: Bolsa de Valores")
    st.markdown("Cotiza el precio internacional del **Maíz** en tiempo real (ajustado al tipo de cambio USD/MXN).")
    
    if st.button("📡 Sincronizar Precio del Maíz con Chicago"):
        with st.spinner("Hackeando la matriz financiera..."):
            try:
                usd_mxn = yf.Ticker("MXN=X")
                precio_dolar = usd_mxn.fast_info['lastPrice']
                
                maiz_ticker = yf.Ticker("ZC=F")
                precio_centavos_bushel = maiz_ticker.fast_info['lastPrice']
                
                precio_usd_bushel = precio_centavos_bushel / 100
                precio_usd_kg = precio_usd_bushel / 25.401
                precio_mxn_kg = precio_usd_kg * precio_dolar
                nuevo_precio_maiz = round(precio_mxn_kg, 2)
                
                llave_maiz = "maiz_molido" if "maiz_molido" in base_datos else list(base_datos.keys())[0]
                
                base_datos[llave_maiz]["costo_kg"] = nuevo_precio_maiz
                
                supabase.table("inventario").update({
                "stock_kg": float(base_datos[llave_maiz]["stock_kg"]),
                "costo_kg": float(base_datos[llave_maiz]["costo_kg"])
            }).eq("insumo", llave_maiz).execute()
            
            
                registrar_bitacora("Radar Chicago", f"Precio del maíz fijado en ${nuevo_precio_maiz} MXN/kg")
                    
                st.success(f"✅ ¡Éxito! Dólar a ${precio_dolar:.2f} MXN. Nuevo precio del Maíz fijado en **${nuevo_precio_maiz} MXN/kg**.")
                import time
                time.sleep(3) 
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Los de traje cortaron la conexión: {e}")

# SÚPER-LABORATORIO
elif "Laboratorio" in opcion or "Perfil" in opcion or "Motor IA" in opcion:
    st.header("🧪 Súper-Laboratorio y Centro de Mando")
    st.markdown("Diseña la genética, audita y optimiza las raciones alimenticias del rancho en una sola pantalla.")
    st.divider()

    # GESTOR DE LOTES INTEGRADO 
    st.subheader("🐄 1. Selección o Creación de Lote")
    
    tab_cargar, tab_crear = st.tabs(["📋 Cargar Lote Activo", "🧬 Crear Nuevo Lote (IA Genética)"])
    
    with tab_cargar:
        col_act, col_ref = st.columns([3, 1])
        
        with col_ref:
            st.button("🔄 Actualizar Lista", use_container_width=True)

        try:
            respuesta = supabase.table("perfiles_lotes").select("*").execute()
            
            lotes_guardados = respuesta.data
            
            if lotes_guardados:
                nombres_lotes = [l["nombre_lote"] for l in lotes_guardados]
                
                with col_act:
                    lote_elegido = st.selectbox("Selecciona el lote con el que trabajarás hoy:", nombres_lotes)
                
                if st.button("⚡ Activar Lote para Formulación", use_container_width=True):
                    datos_lote = next(item for item in lotes_guardados if item["nombre_lote"] == lote_elegido)
                    
                    st.session_state['perfil'] = {
                        "nombre": datos_lote["nombre_lote"],
                        "raza": datos_lote["raza"],
                        "genero": datos_lote["genero"],
                        "proposito": datos_lote["proposito"],
                        "edad": int(datos_lote["edad"]),
                        "peso": float(datos_lote["peso_promedio"]),
                        "clima": float(datos_lote["clima_local"]),
                        "costo_salud": float(datos_lote["costo_salud"])
                    }
                    
                    st.success(f"✅ ¡Lote **{lote_elegido}** activado! Baja a la sección de dietas.")
            
            else:
                st.info("⚠️ No hay animales en la Nube. Ve a la pestaña 'Crear Nuevo Lote'.")
        
        except Exception as e:
            st.error(f"Error con la bóveda de lotes: {e}")


    with tab_crear:
        st.info("💡 Diseña la genética. Al guardar, quedará blindado en la base de datos.")
        
        nombre_nuevo_lote = st.text_input("Dale un nombre a este grupo:")
        
        # LISTA RAZAS
        razas_disponibles = [
            "brahman", "nelore", "sardo negro", "gyr", "indubrasil", "guzerat",
            "angus", "charolais", "simmental", "hereford", "suizo europeo", "holstein", "limousin", "jersey",
            "brangus (brahman x angus)", "braford (brahman x hereford)", "charbray (brahman x charolais)",
            "simbrah (brahman x simmental)", "simangus (simmental x angus)", "black baldy (angus x hereford)",
            "nelangus (nelore x angus)", "suizo-cebu (suizo x brahman)", "girolando (holstein x gyr)",
            "beefmaster", "brahmousin (brahman x limousin)"
        ]

        with st.form("perfil_animal"):
            col1, col2 = st.columns(2)
            
            with col1:
                raza_sel = st.selectbox("1. Raza:", razas_disponibles)
                genero = st.radio("2. Género:", ["Macho", "Hembra"], horizontal=True)
                proposito = st.selectbox("3. Propósito:", ["Carne", "Leche", "Semental", "Doble Propósito"])
            
            with col2:
                edad = st.number_input("4. Edad (meses):", min_value=1, max_value=200, value=5)
                peso = st.number_input("5. Peso (kg):", min_value=30, max_value=1500, value=180)
                clima = st.slider("6. Clima (°C):", 0, 50, 32)
            
            st.markdown("### 💊 Protocolo Sanitario (Opcional)")
            col_med1, col_med2 = st.columns(2)
            with col_med1:
                nombres_desp = ["❌ Ninguno (No aplicar)"] + [d["nombre"] for d in botiquin["desparasitantes"].values()]
                desp_sel = st.selectbox("Desparasitante", nombres_desp)
            with col_med2:
                nombres_vac = ["❌ Ninguna (No aplicar)"] + [d["nombre"] for d in botiquin["vacunas"].values()]
                vac_sel = st.selectbox("Vacuna Base", nombres_vac)

            enviado = st.form_submit_button("🔥 ANALIZAR Y GUARDAR PERFIL GENÉTICO")
        
        if enviado:
            # LÓGICA DE SALUD OPCIONAL
            if desp_sel == "❌ Ninguno (No aplicar)":
                datos_desp = {"dosis_ml_por_kg": 0, "costo_por_ml": 0, "tiempo_retiro_dias": 0}
            else:
                datos_desp = next(d for d in botiquin["desparasitantes"].values() if d["nombre"] == desp_sel)
                
            if vac_sel == "❌ Ninguna (No aplicar)":
                datos_vac = {"dosis_ml_fija": 0, "costo_por_dosis": 0, "tiempo_retiro_dias": 0}
            else:
                datos_vac = next(d for d in botiquin["vacunas"].values() if d["nombre"] == vac_sel)

            dosis_exacta_ml = peso * datos_desp["dosis_ml_por_kg"]
            costo_desp = dosis_exacta_ml * datos_desp["costo_por_ml"]
            costo_vac = datos_vac["costo_por_dosis"]
            
            costo_salud_total = costo_desp + costo_vac
            retiro_dias = max(datos_desp["tiempo_retiro_dias"], datos_vac["tiempo_retiro_dias"])

            st.divider()
            
            st.subheader("🧬 Dictamen de Inteligencia Genética")
            
            raza = raza_sel.lower()
            
            codex_genetico = {
                # BOS INDICUS (Cebú - Trópico)
                "brahman": {"sangre": "Indicus", "clima": "Trópico/Calor Extremo", "riesgo_termico": "Nulo", "proposito": "Carne"},
                "nelore": {"sangre": "Indicus", "clima": "Trópico/Calor Extremo", "riesgo_termico": "Nulo", "proposito": "Carne"},
                "sardo negro": {"sangre": "Indicus", "clima": "Trópico/Humedad", "riesgo_termico": "Nulo", "proposito": "Doble Propósito"},
                "gyr": {"sangre": "Indicus", "clima": "Trópico/Calor", "riesgo_termico": "Nulo", "proposito": "Leche Tropical"},
                "indubrasil": {"sangre": "Indicus", "clima": "Trópico", "riesgo_termico": "Nulo", "proposito": "Carne"},
                "guzerat": {"sangre": "Indicus", "clima": "Trópico/Árido", "riesgo_termico": "Nulo", "proposito": "Doble Propósito"},
                
                # BOS TAURUS (Europeos - Templado) 
                "angus": {"sangre": "Taurus", "clima": "Templado/Frío", "riesgo_termico": "Crítico (>30°C)", "proposito": "Carne Premium"},
                "charolais": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Alto", "proposito": "Carne (Volumen)"},
                "simmental": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Alto", "proposito": "Doble Propósito"},
                "hereford": {"sangre": "Taurus", "clima": "Templado/Frío", "riesgo_termico": "Crítico (>30°C)", "proposito": "Carne Rústica"},
                "suizo europeo": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Moderado", "proposito": "Doble Propósito"},
                "holstein": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Crítico (>28°C)", "proposito": "Leche Especializada"},
                "limousin": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Alto", "proposito": "Carne (Canal)"},
                "jersey": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Moderado", "proposito": "Leche (Grasa)"},
                
                # CRUZAS Y SINTÉTICAS
                "brangus (brahman x angus)": {"sangre": "Sintética", "clima": "Subtrópico", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "braford (brahman x hereford)": {"sangre": "Sintética", "clima": "Subtrópico", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "charbray (brahman x charolais)": {"sangre": "Sintética", "clima": "Trópico Seco", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "simbrah (brahman x simmental)": {"sangre": "Sintética", "clima": "Subtrópico", "riesgo_termico": "Bajo", "proposito": "Doble Propósito"},
                "simangus (simmental x angus)": {"sangre": "Taurus cruzado", "clima": "Templado", "riesgo_termico": "Moderado", "proposito": "Carne"},
                "black baldy (angus x hereford)": {"sangre": "Taurus cruzado", "clima": "Templado/Frío", "riesgo_termico": "Alto", "proposito": "Carne"},
                "nelangus (nelore x angus)": {"sangre": "Sintética", "clima": "Trópico", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "suizo-cebu (suizo x brahman)": {"sangre": "Sintética", "clima": "Trópico Húmedo", "riesgo_termico": "Bajo", "proposito": "Doble Propósito"},
                "girolando (holstein x gyr)": {"sangre": "Sintética", "clima": "Trópico/Humedad", "riesgo_termico": "Bajo", "proposito": "Leche Tropical"},
                "beefmaster": {"sangre": "Sintética", "clima": "Adaptable", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "brahmousin (brahman x limousin)": {"sangre": "Sintética", "clima": "Subtrópico", "riesgo_termico": "Bajo", "proposito": "Carne"}
            }

            datos_raza = codex_genetico.get(raza_sel.lower(), {"sangre": "Desconocida", "clima": "Variable", "riesgo_termico": "Desconocido", "proposito": "General"})

            st.info(f"🧬 **Perfil Genético:** {datos_raza['sangre']} | 🎯 **Propósito:** {datos_raza['proposito']}")

            if clima >= 35 and datos_raza["riesgo_termico"] in ["Crítico (>30°C)", "Crítico (>28°C)"]:
                st.error(f"❌ **INCOMPATIBILIDAD GRAVE:** Un animal {datos_raza['sangre']} a {clima}°C sufrirá estrés térmico severo y caída de producción ({datos_raza['proposito']}).")
            elif clima >= 30 and datos_raza["riesgo_termico"] == "Alto":
                st.warning(f"⚠️ **RIESGO MODERADO:** La temperatura de {clima}°C está en el límite para esta genética. Vigilar sombra e hidratación.")
            elif datos_raza["riesgo_termico"] == "Nulo":
                st.success(f"✅ **ADAPTABILIDAD PERFECTA:** Genética resistente para {datos_raza['clima']}. Soporta bien los {clima}°C.")
            else:
                st.success(f"⚖️ **CLIMA CONFORTABLE:** Temperatura de {clima}°C dentro del rango de confort para su perfil.")

            try:
                st.divider()
                st.subheader("💊 Receta y Tiempos de Retiro")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Desparasitante", f"{dosis_exacta_ml:.1f} ml", f"${costo_desp:.2f} MXN", delta_color="off")
                col_r2.metric("Vacuna Base", f"{datos_vac['dosis_ml_fija']:.1f} ml", f"${costo_vac:.2f} MXN", delta_color="off")
                col_r3.metric("Inversión Sanitaria", f"${costo_salud_total:.2f} MXN")

                if retiro_dias > 0:
                    st.error(f"🛑 **BLOQUEO COMERCIAL:** Los animales NO pueden ir a rastro en los próximos **{retiro_dias} días** debido a residuos en tejidos.")
                else:
                    st.success("✅ **LIBRE DE RESIDUOS:** Comercialización inmediata autorizada.")
            except NameError:
                st.info("👆 Selecciona los medicamentos arriba y presiona 'Analizar y Guardar' para calcular la receta y los tiempos de retiro.")

            if nombre_nuevo_lote:
                try:
                    supabase.table("perfiles_lotes").insert({
                        "nombre_lote": nombre_nuevo_lote,
                        "raza": raza_sel,
                        "genero": genero,
                        "proposito": datos_raza["proposito"],
                        "edad": edad,
                        "peso_promedio": peso,
                        "clima_local": clima,
                        "costo_salud": costo_salud_total
                    }).execute()
                    
                    st.success(f"✅ ¡Guardado! Ve a la pestaña 'Cargar Lote' y presiona el botón 'Actualizar Lista'.")
                
                except Exception as e:
                    st.error(f"Error guardando en la Nube: {e}")
            
            else:
                st.error("⚠️ Debes ponerle un nombre al lote arriba para poder guardarlo.")

    # SISTEMA DE FORMULACIÓN
    if st.session_state.get('perfil') is not None:
        perf = st.session_state['perfil']
        peso = float(perf['peso'])
        clima = float(perf['clima'])

        st.divider()
        st.info(f"🟢 **OPERANDO PARA:** Lote '{perf['nombre']}' | Raza: {perf['raza'].upper()} | Peso: {peso} kg | Clima: {clima}°C")

        st.subheader("🧠 Diagnóstico Nutricional Dinámico (IA)")
        consumo_base = peso * 0.03
        prot_meta = 14.0

        if clima >= 35:
            consumo_real = consumo_base * 0.85
            prot_meta = 16.0
            st.error(f"🚨 **ALERTA DE ESTRÉS CALÓRICO ({clima}°C):** El animal está sofocado. Reducirá su consumo a **{consumo_real:.1f} kg/día**. Se exige concentrar la dieta a **{prot_meta}% de Proteína**.")
        elif clima < 20:
            consumo_real = consumo_base * 1.10
            prot_meta = 12.0
            st.info(f"❄️ **ALERTA DE FRÍO ({clima}°C):** El animal comerá más (**{consumo_real:.1f} kg/día**) para calentarse. Sugerimos bajar proteína a **{prot_meta}%** y subir energía.")
        else:
            consumo_real = consumo_base
            st.success(f"✅ **CLIMA CONFORTABLE ({clima}°C):** Consumo normal proyectado de **{consumo_real:.1f} kg/día**. Meta sugerida: **{prot_meta}% de Proteína**.")

        tab_manual, tab_ia = st.tabs(["🛠️ Formulación Manual", "🤖 Piloto Automático (Motor IA)"])

        
        with tab_manual:
            st.markdown("### ⚖️ Auditoría de Mezcla Manual")
            
            filtro = st.radio("Filtrar ingredientes por aporte principal:", ("Todos", "Alta Proteína (>20%)", "Alta Energía (>2.8 Mcal)", "Alta Fibra (>20%)"), horizontal=True)

            lista_filtrada = []
            for insumo, datos in base_datos.items():
                if filtro == "Todos": lista_filtrada.append(insumo)
                elif "Proteína" in filtro and datos.get("proteina_pct", 0) >= 20.0: lista_filtrada.append(insumo)
                elif "Energía" in filtro and datos.get("energia_mcal", 0) >= 2.8: lista_filtrada.append(insumo)
                elif "Fibra" in filtro and datos.get("fibra_pct", 0) >= 20.0: lista_filtrada.append(insumo)

            if not lista_filtrada: st.warning("No hay insumos en tu bodega que cumplan este filtro.")

            if "receta_guardada_ia" in st.session_state:
                st.success("🤖 Receta de la IA detectada en la memoria.")
                if st.button("📥 Importar Receta a la Mesa de Trabajo", key="btn_importar_unica"):
                    st.session_state["memoria_selector"] = st.session_state["receta_guardada_ia"]["ingredientes"]
                    for ins, kg in st.session_state["receta_guardada_ia"]["kilos"].items():
                        st.session_state[f"kg_{ins}"] = kg

            seleccionados = st.multiselect("Seleccione los ingredientes a utilizar:", lista_filtrada, key="memoria_selector")

            mezcla_final = []
            total_kilos_mezcla = 0

            if seleccionados:
                cols = st.columns(len(seleccionados))
                for i, insumo in enumerate(seleccionados):
                    with cols[i]:
                        kilos = st.number_input(f"Kg de {insumo}", min_value=0.0, step=1.0, key=f"kg_{insumo}")
                        mezcla_final.append({"nombre": insumo, "kilos": kilos, "datos": base_datos[insumo]})
                        total_kilos_mezcla += kilos

            if st.button("⚖️ AUDITAR MEZCLA MANUAL"):
                if total_kilos_mezcla > 0:
                    prot_acum = sum((item["kilos"] * item["datos"]["proteina_pct"]) for item in mezcla_final) / total_kilos_mezcla
                    ener_acum = sum((item["kilos"] * item["datos"]["energia_mcal"]) for item in mezcla_final) / total_kilos_mezcla
                    fibr_acum = sum((item["kilos"] * item["datos"]["fibra_pct"]) for item in mezcla_final) / total_kilos_mezcla
                    costo_tot = sum((item["kilos"] * item["datos"]["costo_kg"]) for item in mezcla_final)

                    st.session_state['mezcla'] = {
                        "proteina": prot_acum, "energia": ener_acum, "fibra": fibr_acum,
                        "costo_total": costo_tot, "total_kilos": total_kilos_mezcla,
                        "costo_kg": costo_tot / total_kilos_mezcla, "detalle": mezcla_final
                    }
                    st.success("✅ Auditoría completada")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Proteína Cruda", f"{prot_acum:.2f}%")
                    c2.metric("Energía Metab.", f"{ener_acum:.2f} Mcal")
                    c3.metric("Fibra (FDN)", f"{fibr_acum:.2f}%")

                    st.divider()
                    st.subheader("📊 Radiografía Detallada por Insumo")
                    datos_desglose = []
                    for item in mezcla_final:
                        kg_ingrediente = item["kilos"]
                        pct_mezcla = (kg_ingrediente / total_kilos_mezcla) * 100
                        kg_proteina = kg_ingrediente * (item["datos"]["proteina_pct"] / 100)
                        datos_desglose.append({
                            "Insumo": item["nombre"].upper(), "Participación (%)": round(pct_mezcla, 2),
                            "Aporte Proteína (kg)": round(kg_proteina, 2), "Costo en Mezcla ($)": round(kg_ingrediente * item["datos"]["costo_kg"], 2)
                        })

                    df_desglose = pd.DataFrame(datos_desglose)
                    st.dataframe(df_desglose, use_container_width=True)
                    
                    if prot_acum > 18.0: st.warning("⚠️ RIESGO: Nivel de proteína muy alto. Podría causar estrés renal.")
                    elif fibr_acum < 10.0: st.warning("⚠️ RIESGO: Fibra muy baja. Peligro inminente de acidosis ruminal.")

                    st.session_state['mezcla_lista'] = {
                        "total_kilos": float(total_kilos_mezcla), "costo_total": float(costo_tot), "proteina": float(prot_acum)
                    }
                else:
                    st.error("Agregue kilos a los ingredientes.")

            if 'mezcla_lista' in st.session_state:
                st.divider()
                if st.button("💾 Procesar Lote Manual y Registrar Gasto", use_container_width=True):
                    m = st.session_state['mezcla_lista']
                    detalle_txt = f"Lote MANUAL de {m['total_kilos']}kg al {m['proteina']:.1f}% de proteína."
                    try:
                        supabase.table("bitacora").insert({"accion": "Preparación Manual", "detalle": detalle_txt, "gasto_total": m['costo_total'], "kilos_procesados": m['total_kilos']}).execute()
                        st.success(f"✅ ¡Dinero auditado! Se registraron ${m['costo_total']:,.2f} MXN en la Nube.")
                        del st.session_state['mezcla_lista']
                    except Exception as e:
                        st.error(f"⚠️ Error al conectar con la bóveda: {e}")

            st.divider()
            st.subheader("⚖️ Corrector de Mezcla (Cuadrado de Pearson)")
            
            opciones_ingredientes = list(base_datos.keys())
            
            if not opciones_ingredientes:
                st.warning("⚠️ Bodega vacía. Agrega insumos para usar el corrector.")
            else:
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    prot_actual = st.number_input("Proteína actual de la mezcla (%)", value=11.0, step=0.5)
                    kilos_en_tolva = st.number_input("Kilos actuales en la revolvedora", value=1000, step=100)
                with col_p2:
                    prot_objetivo = st.number_input("Proteína objetivo (%)", value=14.0, step=0.5)
                    ing_refuerzo = st.selectbox("Selecciona ingrediente de refuerzo:", opciones_ingredientes)
                
                if ing_refuerzo:
                    prot_refuerzo = base_datos[ing_refuerzo].get("proteina_pct", 0)

                    if st.button("🧮 Calcular Corrección"):
                        if prot_objetivo <= prot_actual or prot_objetivo >= prot_refuerzo:
                            st.error("❌ Misión Imposible: La proteína objetivo debe estar ENTRE la actual y la del refuerzo.")
                        else:
                            partes_refuerzo = abs(prot_objetivo - prot_actual)
                            partes_mezcla = abs(prot_refuerzo - prot_objetivo)
                            kilos_a_añadir = (kilos_en_tolva / partes_mezcla) * partes_refuerzo
                            st.success(f"**Resultado:** Añade **{kilos_a_añadir:.2f} kg** de **{ing_refuerzo.upper()}** para lograr el {prot_objetivo}%.")

        # PESTAÑA: MOTOR IA
        with tab_ia:
            st.subheader("📊 Radar de Costo-Beneficio (Proteína Barata)")
            analisis_prot = []
            for ins, datos in base_datos.items():
                if datos.get("proteina_pct", 0) > 2.0:
                    costo_por_punto = datos["costo_kg"] / datos["proteina_pct"]
                    analisis_prot.append({
                        "Insumo": ins.title().replace("_", " "), "Costo por Punto": f"${costo_por_punto:.2f}",
                        "Proteína Total": f"{datos['proteina_pct']}%", "Costo x Kg": f"${datos['costo_kg']:.2f}"
                    })
            st.dataframe(sorted(analisis_prot, key=lambda x: float(x["Costo por Punto"].replace('$', ''))), use_container_width=True)
            st.divider()

            st.markdown("### 🎛️ Motor de Optimización Lineal")
            col_sis, col_etapa = st.columns(2)
            with col_sis: sistema = st.radio("1. Sistema de Producción:", ["🏡 Estabulado (Corral)", "🌿 Pastoreo (Suplemento)"])
            with col_etapa: etapa = st.selectbox("2. Etapa de Vida:", ["🍼 Inicio (Desarrollo de Rumen)", "📈 Desarrollo (Crecimiento)", "🥩 Finalización"])

            usar_promotores = st.toggle("💊 Incluir Promotores / Ionóforos (Ej. Monensina)")
            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                req_proteina = st.number_input("🎯 Objetivo de Proteína (%)", min_value=5.0, max_value=30.0, value=float(prot_meta), step=0.5)
            with col2:
                req_energia = st.number_input("⚡ Objetivo de Energía (Mcal)", min_value=1.0, max_value=4.0, value=2.5, step=0.1)


            if st.button("🧠 GENERAR FÓRMULA ÓPTIMA"):
                prob = pulp.LpProblem("Dieta_Barata", pulp.LpMinimize)
                insumos = list(base_datos.keys())
                x = pulp.LpVariable.dicts("Ingrediente", insumos, lowBound=0)

                prob += pulp.lpSum([x[i] * base_datos[i]["costo_kg"] for i in insumos]), "Costo"
                prob += pulp.lpSum([x[i] for i in insumos]) == 100, "Peso_100"
                prob += pulp.lpSum([x[i] * base_datos[i]["proteina_pct"] for i in insumos]) >= req_proteina * 100, "Req_Prot"
                prob += pulp.lpSum([x[i] * base_datos[i]["energia_mcal"] for i in insumos]) >= req_energia * 100, "Req_Ener"

                for i in insumos:
                    if "max_pct" in base_datos[i]:
                        prob += x[i] <= base_datos[i]["max_pct"], f"Max_{i}"

                toxicos = [i for i in ["urea_agricola", "pollinaza", "harina_pescado"] if i in insumos]
                if "urea_agricola" in toxicos: prob += x["urea_agricola"] <= 0.5, "Tope_Urea"
                if "pollinaza" in toxicos: prob += x["pollinaza"] <= 12.0, "Tope_Pollinaza"
                if "harina_pescado" in toxicos: prob += x["harina_pescado"] <= 4.0, "Tope_Pescado"
                if len(toxicos) >= 2: prob += pulp.lpSum([x[i] for i in toxicos]) <= 11.0, "Colchon_Paranoia_Palatabilidad"

                prob.solve()

                if pulp.LpStatus[prob.status] == "Optimal":
                    resultados = []
                    costo_cien_kg = 0
                    for i in insumos:
                        if x[i].varValue > 0.01:
                            costo_ing = x[i].varValue * base_datos[i]["costo_kg"]
                            costo_cien_kg += costo_ing
                            resultados.append({
                                "Insumo": i.upper(), "Kilos por 100kg": round(x[i].varValue, 2),
                                "Costo ($)": round(costo_ing, 2)
                            })

                    st.session_state['solucion_ia'] = {
                        "df": pd.DataFrame(resultados), "costo_kg": costo_cien_kg / 100,
                        "detalles_ia": { "ingredientes": [i for i in insumos if x[i].varValue > 0.01], "kilos": {i: float(x[i].varValue) for i in insumos if x[i].varValue > 0.01} },
                        "proteina_log": req_proteina, "energia_log": req_energia
                    }
                    st.balloons()
                else:
                    st.session_state['solucion_ia'] = None
                    st.error("❌ Misión Imposible. Faltan ingredientes para esta meta.")

            if 'solucion_ia' in st.session_state and st.session_state['solucion_ia'] is not None:
                sol = st.session_state['solucion_ia']

                st.success("✅ ¡Fórmula óptima encontrada!")
                st.title(f"💰 Costo final proyectado: ${sol['costo_kg']:.2f} MXN / kg")
                st.dataframe(sol['df'], use_container_width=True, hide_index=True)

                st.divider()
                st.markdown("### 🚜 Auto-Formulador de Lote (Revolvedora IA)")
                st.info(f"Usando el consumo biológico calculado: **{consumo_real:.1f} kg/día** por animal.")

                with st.form("form_tolva_ia"):
                    c_lote1, c_lote2 = st.columns(2)
                    with c_lote1: num_cabezas = st.number_input("Número de Animales a alimentar:", min_value=1, value=50, step=5)
                    with c_lote2: dias_dieta = st.number_input("¿Para cuántos días vas a preparar?", min_value=1, value=3, step=1)
                    
                    btn_tolva = st.form_submit_button("🤖 Generar Receta de Tolva y Pagar Lote", use_container_width=True)

                if btn_tolva:
                    kilos_totales_ia = num_cabezas * consumo_real * dias_dieta
                    costo_lote_ia = kilos_totales_ia * sol['costo_kg']

                    st.success(f"✅ **¡Tolva Calculada!** Mezcla exactamente esto en tu revolvedora para **{kilos_totales_ia:,.0f} kg** totales:")

                    receta_tolva = []
                    for index, row in sol['df'].iterrows():
                        kg_insumo_tolva = (row["Kilos por 100kg"] / 100) * kilos_totales_ia
                        receta_tolva.append({"Insumo": row["Insumo"], "Kilos a echar a la Tolva": round(kg_insumo_tolva, 1)})

                    st.dataframe(pd.DataFrame(receta_tolva), use_container_width=True, hide_index=True)
                    st.metric("💰 Costo Total del Lote", f"${costo_lote_ia:,.2f} MXN")

                    try:
                        detalle = f"Lote IA Tolva: {kilos_totales_ia:,.0f}kg al {sol['proteina_log']}% de prot."
                        supabase.table("bitacora").insert({"accion": "Preparación IA", "detalle": detalle, "gasto_total": costo_lote_ia, "kilos_procesados": kilos_totales_ia}).execute()

                        st.session_state['mezcla'] = {
                            "proteina": sol['proteina_log'], "energia": sol['energia_log'], "fibra": 10.0,
                            "costo_total": costo_lote_ia, "total_kilos": kilos_totales_ia,
                            "costo_kg": sol['costo_kg'], "detalle": "Fórmula IA Optimizada"
                        }
                        st.success(f"✅ ¡Gastos Registrados! Ya puedes ir al Módulo 4: Proyecciones Financieras.")
                    except Exception as e:
                        st.error(f"⚠️ Error al registrar en la bóveda: {e}")

# PROYECCIÓN FINANCIERA
elif "Proyección" in opcion:
    st.header("📈 Centro de Control Financiero")
    if 'perfil' not in st.session_state or 'mezcla' not in st.session_state:
        st.error("⚠️ Datos incompletos. Por favor, configure la genética y la dieta de los animales directamente en el **Súper-Laboratorio** para calcular la rentabilidad.")
    else:
        perf = st.session_state['perfil']
        mezc = st.session_state['mezcla']
        
        ganancia_est = 0.8 + ((mezc["proteina"] - 14.0) * 0.05)
        consumo_diario = perf["peso"] * 0.03
        costo_salud_amortizado = perf.get("costo_salud", 0) / 100
        costo_dia = consumo_diario * mezc["costo_kg"]
        costo_kg_carne = costo_dia / ganancia_est
        
        #INTELIGENCIA DE PRECIOS Y ESTRATEGIA DE SALIDA
        st.subheader("📈 Estrategia de Engorda y Salida")
        
        tipo_meta = st.radio("¿Cuál es tu objetivo de engorda para este lote?", ["🎯 Meta por Peso (Vender a los X kilos)", "⏳ Meta por Tiempo (Vender a los X meses)"], horizontal=True)
        
        if "Peso" in tipo_meta:
            meta_obj = st.number_input("Peso Objetivo de Venta (kg):", min_value=float(perf["peso"])+10.0, value=300.0, step=10.0)
            dias_faltantes = (meta_obj - perf["peso"]) / ganancia_est
            st.info(f"⏳ A este ritmo, llegarás a los **{meta_obj} kg** en aprox. **{dias_faltantes:.0f} días** ({dias_faltantes/30:.1f} meses).")
        else:
            meta_obj = st.number_input("Tiempo máximo en corral (Meses):", min_value=1.0, value=6.0, step=0.5)
            peso_final_proy = perf["peso"] + ((meta_obj * 30) * ganancia_est)
            st.info(f"⚖️ A este ritmo, al cumplir los **{meta_obj} meses**, el animal pesará aprox. **{peso_final_proy:.1f} kg**.")

        st.divider()
        st.subheader("💰 Inteligencia de Mercado (El Semáforo de Rentabilidad)")
        
        col_m1, col_m2, col_m3 = st.columns(3)

        with col_m1:
            precio_venta = st.number_input("Precio de Venta en Pie ($/kg):", min_value=10.0, value=85.0, step=1.0)
            
        # LA REGLA DE ORO DE LOS $50 PESOS
        ingreso_bruto_diario = ganancia_est * precio_venta
        ganancia_neta_diaria = ingreso_bruto_diario - costo_dia
        margen_por_kilo = precio_venta - costo_kg_carne

        with col_m2:
            st.metric("Costo Producción (por kg)", f"${costo_kg_carne:.2f}/kg")

        with col_m3:
            if ganancia_neta_diaria >= 50:
                st.metric("Utilidad Neta Diaria", f"${ganancia_neta_diaria:.2f}/día", delta="¡SÚPER RENTABLE!")
            elif ganancia_neta_diaria > 0:
                st.metric("Utilidad Neta Diaria", f"${ganancia_neta_diaria:.2f}/día", delta="Rentabilidad Baja", delta_color="off")
            else:
                st.metric("Utilidad Neta Diaria", f"${ganancia_neta_diaria:.2f}/día", delta="PÉRDIDA", delta_color="inverse")

        # AUDITORÍA FIRA
        if ganancia_neta_diaria >= 50:
            st.success("✅ **APROBADO (Estándar de Alta Eficiencia):** El animal genera $50 o más libres al día. Excelente conversión económica.")
        elif ganancia_neta_diaria > 0:
            st.warning("⚠️ **RIESGO DE RETENCIÓN:** Generas ganancia, pero por debajo de los $50 diarios. Si se alarga la engorda, el costo de mantenimiento te comerá el negocio.")
        else:
            st.error("❌ **ALERTA ROJA DE QUIEBRA:** El animal te está costando más de lo que produce. Cambia la mezcla o vende lo más pronto posible.")

        #FICHA TÉCNICA VISUAL
        st.divider()
        st.subheader("📄 Ficha Técnica para Inversionistas")
        
        color_borde = "#4CAF50" if margen_por_kilo > 0 else "#F44336"
        estatus = "🟢 NEGOCIO RENTABLE" if margen_por_kilo > 0 else "🔴 ALERTA DE PÉRDIDA"
        
        ficha_html = f"""
        <div style="background-color: #1E1E1E; padding: 25px; border-radius: 15px; border: 2px solid {color_borde}; color: white; font-family: sans-serif;">
            <h2 style="color: {color_borde}; margin-top: 0;">📦 REPORTE DE ENGORDA: {perf['raza'].upper()}</h2>
            <p style="font-size: 14px; color: #AAA; margin-top: -15px;">ESTATUS: {estatus}</p>
            <hr style="border: 0.5px solid #444;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Peso Actual:</b></td><td>{perf['peso']} kg</td></tr>
                <tr><td><b>Proteína Dieta:</b></td><td>{mezc['proteina']:.2f}%</td></tr>
                <tr><td><b>Ganancia Diaria:</b></td><td>{ganancia_est:.2f} kg/día</td></tr>
                <tr><td><b>Precio Venta Mercado:</b></td><td>${precio_venta:.2f} MXN/kg</td></tr>
            </table>
            <br>
            <div style="display: flex; justify-content: space-between; gap: 10px;">
                <div style="background-color: #2D2D2D; padding: 15px; border-radius: 10px; width: 50%; text-align: center;">
                    <span style="font-size: 12px; color: #AAA;">COSTO PRODUCIR 1 KG</span><br>
                    <span style="font-size: 24px; font-weight: bold; color: white;">${costo_kg_carne:.2f}</span>
                </div>
                <div style="background-color: #2D2D2D; padding: 15px; border-radius: 10px; width: 50%; text-align: center;">
                    <span style="font-size: 12px; color: #AAA;">UTILIDAD NETA POR KG</span><br>
                    <span style="font-size: 24px; font-weight: bold; color: {color_borde};">${margen_por_kilo:.2f}</span>
                </div>
            </div>
            <p style="font-size: 12px; color: #777; margin-top: 15px; text-align: right;">Generado por AgroIA v3.1</p>
        </div>
        """
        st.markdown(ficha_html, unsafe_allow_html=True)
        
        if margen_por_kilo > 15:
            st.balloons()

# BOTÓN DE CAJA NEGRA
        st.divider()
        st.subheader("💾 Respaldar Lote")
        if st.button("Guardar en la Caja Negra"):
            try:
                nuevo_registro = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Raza": perf['raza'].upper(),
                    "Costo Producción": round(costo_kg_carne, 2),
                    "Precio Venta": round(precio_venta, 2),
                    "Margen Utilidad": round(margen_por_kilo, 2)
                }
                
                registrar_bitacora("Proyección Financiera", 
                                 f"Raza: {perf['raza'].upper()} | Margen: ${round(margen_por_kilo, 2)}/kg | Costo Prod: ${round(costo_kg_carne, 2)}/kg")
                
                st.success("✅ ¡Proyección guardada en la Caja Negra de la nube!")
                
            except Exception as e:
                st.error(f"Error al guardar la proyección: {e}")
    
# CAJA NEGRA
elif "Caja Negra" in opcion:
    st.header("📓 Caja Negra: Historial de Movimientos")
    st.markdown("Auditoría en tiempo real de las operaciones del rancho.")
# DASHBOARD FINANCIERO 
    st.subheader("📈 Resumen de Operación (Mensual)")
    
    # Tarjetas de Métricas Rápidas
    kpi1, kpi2, kpi3 = st.columns(3)
    
    kpi1.metric(
        label="💰 Gasto Total en Alimento", 
        value="$45,230 MXN", 
        delta="-$2,100 (Ahorro vs mes pasado)", 
        delta_color="inverse"
    )
    kpi2.metric(
        label="🔄 Lotes Preparados", 
        value="14 Lotes", 
        delta="+2 lotes", 
        delta_color="normal"
    )
    kpi3.metric(
        label="📉 Costo Promedio Dieta", 
        value="$4.15 / Kg", 
        delta="-$0.12 centavos", 
        delta_color="inverse"
    )
    
    st.divider()

    try:
        respuesta = supabase.table("bitacora").select("*").order("fecha", desc=True).execute()
        if respuesta.data:
            df_bitacora = pd.DataFrame(respuesta.data)
            df_bitacora['fecha'] = pd.to_datetime(df_bitacora['fecha'])
            
            df_gastos = df_bitacora[df_bitacora['gasto_total'] > 0]
            
            col_graf1, col_graf2 = st.columns(2)
            with col_graf1:
                st.markdown("**💸 Flujo de Capital por Acción**")
                if not df_gastos.empty:
                    fig_bar = px.bar(df_gastos, x='accion', y='gasto_total', color='accion', title="Dinero Invertido/Perdido")
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Aún no hay gastos registrados.")
                    
            with col_graf2:
                st.markdown("**📅 Tendencia de Inversión**")
                if not df_gastos.empty:
                    df_tiempo = df_gastos.groupby(df_gastos['fecha'].dt.date)['gasto_total'].sum().reset_index()
                    fig_line = px.line(df_tiempo, x='fecha', y='gasto_total', markers=True, title="Gasto Histórico")
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("Aún no hay tendencia.")
    except Exception as e:
        st.error(f"Falla de despliegue en Caja Negra: {e}")
        
    st.divider()
    
    try:
        respuesta = supabase.table("bitacora").select("*").order("fecha", desc=True).execute()
        
        if respuesta.data:
            df_bitacora = pd.DataFrame(respuesta.data)
            df_bitacora['fecha'] = pd.to_datetime(df_bitacora['fecha'])
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                fig_pie = px.pie(df_bitacora, names='accion', title='📊 Distribución de Actividades',
                               hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_g1:
                paleta_agro = ['#2ecc71', '#f39c12', '#7f8c8d', '#34495e', '#1abc9c']
                fig_pie = px.pie(df_bitacora, names='accion', title='📊 Distribución de Actividades',
                               hole=0.4, color_discrete_sequence=paleta_agro)
                fig_pie.update_traces(textinfo='percent+label', textposition='inside')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.divider()
            
            df_bitacora['fecha_str'] = df_bitacora['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df_final = df_bitacora[['fecha_str', 'accion', 'detalle']]
            df_final.columns = ['Fecha y Hora', 'Tipo de Acción', 'Detalle del Movimiento']
            
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            st.divider()
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Historial a Excel (CSV)",
                data=csv,
                file_name=f'Auditoria_Rancho_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info("La bitácora está limpia. Aún no hay movimientos registrados.")
            
    except Exception as e:
        st.error(f"Error al leer la Caja Negra: {e}")
            
# GESTIÓN DE MORTANDAD Y BAJAS
elif "Mortandad" in opcion:
    st.header("🪦 Gestor de Mortandad y Pérdidas")
    st.markdown("Registra las bajas del rebaño para dar de baja las 'bocas que alimentar' y calcular la fuga de capital.")

    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.subheader("Datos de la Baja")
        bajas = st.number_input("Número de cabezas perdidas", min_value=1, value=1, step=1)
        causa = st.selectbox("Causa principal", [
            "Enfermedad (ej. Anemia/Garrapata)", 
            "Clima extremo", 
            "Depredador/Accidente", 
            "Causa Desconocida"
        ])
        peso_estimado = st.number_input("Peso estimado al morir (kg)", min_value=10.0, value=150.0, step=10.0)

    with col_m2:
        st.subheader("Auditoría Financiera")
        st.info("💡 **El Switch del Dinero:** Si ya habías invertido en sus vacunas, ese dinero se va a pérdidas.")
        
        vacunados = st.radio("¿Estos animales ya tenían su protocolo sanitario aplicado?", [
            "🔴 Sí (Se pierde la inversión médica)", 
            "🟢 No (Murieron antes de gastar en ellos)"
        ])

    if st.button("🚨 Registrar Baja Oficial", use_container_width=True):
        perdida_medica = 0
        
        if "Sí" in vacunados:
            if 'perfil' in st.session_state and "costo_salud" in st.session_state['perfil']:
                costo_unitario = st.session_state['perfil']['costo_salud']
            else:
                costo_unitario = 50.0 
            
            perdida_medica = bajas * costo_unitario

        detalle = f"Baja de {bajas} cabezas por {causa}. Fuga de capital médico: ${perdida_medica:.2f}"
        registrar_bitacora("Baja por Mortandad", detalle)
        
        if 'fuga_capital' not in st.session_state:
            st.session_state['fuga_capital'] = 0.0
        st.session_state['fuga_capital'] += perdida_medica

        st.error(f"⚠️ Se dio de baja a {bajas} animal(es). Ya no se contarán para la compra de alimento.")
        
        if perdida_medica > 0:
            st.warning(f"💸 Fuga de capital registrada: Se perdieron **${perdida_medica:.2f} MXN** en medicinas que no se van a recuperar.")
        else:
            st.success("✅ Baja registrada. Afortunadamente no se había invertido dinero médico en estos animales.")
            
# CONTROL DE PESO (BÁSCULA)
elif "Peso" in opcion:
    st.header("⚖️ Báscula y Rendimiento")
    st.markdown("Registra el peso real para auditar si la dieta está dando los resultados proyectados.")

    modo_campo = st.toggle("📱 Activar Modo Campo (Pantalla para Celular)")

    es_horizontal = False if modo_campo else True
    tipo_pesaje = st.radio("Método de captura:", ["📊 Promedio por Lote", "🏷️ Individual (Por Arete)"], horizontal=es_horizontal)

    if modo_campo:
        col_b1 = st.container()
        col_b2 = st.container()
        
        st.markdown("<style> div.stButton > button {height: 4.5rem !important; font-size: 22px !important; border: 2px solid #4CAF50;} </style>", unsafe_allow_html=True)
    else:
        col_b1, col_b2 = st.columns(2)

    with col_b1:
        if "Individual" in tipo_pesaje:
            id_animal = st.text_input("ID o Número de Arete", placeholder="Ej. Becerro 405")
        else:
            id_animal = st.text_input("Nombre del Lote", placeholder="Ej. Corral Norte")

        peso_anterior = st.number_input("Peso Anterior (kg)", min_value=1.0, value=180.0, step=10.0)
        peso_actual = st.number_input("Peso Actual (kg)", min_value=1.0, value=200.0, step=10.0)

    with col_b2:
        dias_transcurridos = st.number_input("Días transcurridos entre pesadas", min_value=1, value=15, step=1)
        meta_sugerida = 1.5
        if 'mezcla' in st.session_state:
            meta_sugerida = 0.8 + ((st.session_state['mezcla'].get("proteina", 14.0) - 14.0) * 0.05)

        meta_ia = st.number_input("Meta de ganancia diaria proyectada (kg/día)", value=float(round(meta_sugerida, 2)), step=0.1)

    if st.button("⚖️ Calcular y Registrar Pesada", use_container_width=True):
        if not id_animal:
            st.error("⚠️ Ponle un nombre al Lote o un número al Arete para registrarlo.")
        elif peso_actual <= peso_anterior:
            st.error("⚠️ El peso actual no puede ser menor o igual al anterior. Revisa los datos.")
        else:
            # Calcular GDP (Ganancia Diaria de Peso)
            gdp_real = (peso_actual - peso_anterior) / dias_transcurridos

            st.divider()
            st.subheader("📈 Diagnóstico de Rendimiento")

            c_res1, c_res2, c_res3 = st.columns(3)
            c_res1.metric("Ganancia Total", f"{peso_actual - peso_anterior:.1f} kg")
            c_res2.metric("Ganancia Diaria (Real)", f"{gdp_real:.2f} kg/día", delta=round(gdp_real - meta_ia, 2))
            c_res3.metric("Meta Proyectada", f"{meta_ia:.2f} kg/día")

            if gdp_real >= meta_ia:
                st.success("✅ **EXCELENTE:** El desempeño supera o iguala la proyección de la dieta. ¡Buen trabajo!")
            elif gdp_real >= meta_ia * 0.8:
                st.warning("⚠️ **ALERTA LEVE:** Están ganando peso, pero un poco por debajo de la meta. Revisa el consumo en comederos.")
            else:
                st.error("❌ **PELIGRO:** Los animales están estancados. Revisa sanidad, estrés por clima o corrige la dieta (Módulo 3).")

            detalle = f"Pesada {id_animal}: {peso_actual}kg. GDP: {gdp_real:.2f}kg/día (Meta: {meta_ia})."
            registrar_bitacora("Control de Peso", detalle)
            if 'perfil' in st.session_state:
                st.session_state['perfil']['peso'] = peso_actual
                st.success(f"🔄 ¡Sistema Nervioso Activo! El peso base para tus finanzas se actualizó automáticamente a {peso_actual} kg.")

# 👑 MÓDULO: BÓVEDA PREMIUM DE GANADERÍA REGENERATIVA & RESILIENCIA GLOBAL
elif "Bóveda" in opcion:
    st.title("👑 Bóveda Premium: Hub Global de Tecnologías Resilientes")
    st.markdown("""
        Este módulo recopila sistemas de manejo y optimización de recursos forrajeros validados en ecosistemas de alta adversidad climatológica. Diseñado para reducir la dependencia de insumos externos y mitigar los efectos de sequías prolongadas mediante protocolos operativos estandarizados.
    """)

    # Selector de los 3 Pilares de Impacto Global
    pilar_seleccionado = st.selectbox(
        "🌍 Seleccione un Pilar de Resiliencia:",
        [
            "🌵 Pilar 1: Resiliencia Extrema y Escasez (Supervivencia Hídrica y Alimentaria)",
            "🦠 Pilar 2: Suelo, Microbiología y Reducción de Insumos (Regeneración)",
            "📡 Pilar 3: Escalabilidad y Manejo Dinámico (Procesos y Tecnología)"
        ]
    )

    st.divider()

    # 🌵 PILAR 1: RESILIENCIA EXTREMA Y ESCASEZ
    if "Pilar 1" in pilar_seleccionado:
        st.subheader("🛡️ Tácticas de Supervivencia ante Sequías e Inflación de Insumos")
        
        tech_p1 = st.radio(
            "Seleccione la Tecnología a Desplegar:",
            ["🌵 Bio-Fábrica de Nopal Forrajero", "🌱 Cultivo Rústico de Azolla", "🌾 Enriquecimiento de Esquilmos (Silo de Tamo)"],
            horizontal=True
        )
        
        st.divider()
        
        # MODULO NOPAL FORRAJERO
        if "Nopal Forrajero" in tech_p1:
            st.markdown("### 🌵 Bio-Fábrica de Nopal Forrajero")
            st.caption("📍 Origen de validación: Zonas semiáridas y Nordeste Brasileño")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "BAJO", "Baja inversión de capital", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "EXCELENTE", "Disponibilidad de material vegetativo local", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "BAJA", "Requiere mano de obra estándar", delta_color="off")
            
            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Calculadora de Racionamiento AgroIA"])
            
            with tab_info:
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Déficit hídrico severo o ausencia de agua de bebida circulante.
                        * Escasez de forraje verde de alta energía en pastoreo.
                        * Estrategia de mantenimiento estacional para ganado bovino de cría.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * **RESTRICCIÓN:** No suministrar pencas de nopal de forma exclusiva. El exceso de agua libre y mucílago genera tránsito intestinal acelerado (diarrea mecánica), provocando deshidratación y pérdida de peso.
                        * **OBLIGATORIEDAD:** Integrar siempre una fuente de fibra larga seca (tamo, rastrojo o paja) para asegurar la rumia correcta.
                    """)
                
                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Cosecha:** Cortar pencas maduras (evitar brotes tiernos por exceso de acidez).
                    2. **Acondicionamiento:** Eliminar espinas mediante chamuscado rápido con quemador de gas.
                    3. **Procesamiento:** Picar en fragmentos de aproximadamente 3x3 cm para facilitar la prensión.
                    4. **Homogeneización:** Mezclar uniformemente con la fracción de fibra seca calculada en la pestaña contigua.
                """)
                
            with tab_receta:
                st.markdown("#### 🧮 Optimización de Dieta de Emergencia y Retorno de Inversión (ROI)")
                st.write("Determine los requerimientos diarios y evalúe el impacto financiero de la contingencia:")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    num_animales = st.number_input("Número de animales en el lote:", min_value=1, value=50, step=1)
                with col_c2:
                    peso_promedio = st.number_input("Peso vivo promedio (kg):", min_value=50, value=400, step=10)
                with col_c3:
                    dias_periodo = st.number_input("Días estimados de contingencia:", min_value=1, value=60, step=5)
                
                consumo_total_fresco_dia = peso_promedio * 0.10
                nopal_por_animal_dia = consumo_total_fresco_dia * 0.75
                tamo_por_animal_dia = consumo_total_fresco_dia * 0.25
                
                total_nopal_necesario = nopal_por_animal_dia * num_animales * dias_periodo
                total_tamo_necesario = tamo_por_animal_dia * num_animales * dias_periodo
                
                st.subheader("📊 Requerimientos Totales de Suministro")
                col_r1, col_r2 = st.columns(2)
                
                with col_r1:
                    st.info(f"🌵 **Nopal Forrajero requerido:**\n* **Por animal/día:** {nopal_por_animal_dia:.1f} kg\n* **Total Periodo:** {total_nopal_necesario / 1000:.2f} Toneladas")
                with col_r2:
                    st.success(f"🌾 **Tamo / Rastrojo requerido:**\n* **Por animal/día:** {tamo_por_animal_dia:.1f} kg\n* **Total Periodo:** {total_tamo_necesario / 1000:.2f} Toneladas")
                
                st.divider()
                
                # CALCULADORA ROI FINANCIERO NOPAL
                st.markdown("#### 💵 Impacto Financiero y Retorno Operativo")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    costo_ton_tamo = st.number_input("Costo de Tamo/Rastrojo por Tonelada ($):", min_value=100, value=1500, step=100)
                    
                    st.markdown("**🚜 Desglose Operativo (Extracción de Nopal)**")
                    jornal_diario = st.number_input("Pago diario al trabajador ($):", min_value=100, value=350, step=50)
                    gasto_gas_gasolina = st.number_input("Gasto diario en Gasolina/Gas LP ($):", min_value=0, value=150, step=50)
                    toneladas_dia = st.number_input("Toneladas recolectadas por día:", min_value=0.5, value=2.0, step=0.5)
                    
                    costo_corte_nopal = (jornal_diario + gasto_gas_gasolina) / toneladas_dia if toneladas_dia > 0 else 0
                    st.caption(f"Costo operativo automatizado: **${costo_corte_nopal:.2f} / Tonelada**")
                    
                with col_f2:
                    costo_ton_paca = st.number_input("Costo de Paca Comercial por Tonelada ($):", min_value=1000, value=5000, step=100)
                
                costo_total_resiliencia = ((total_nopal_necesario / 1000) * costo_corte_nopal) + ((total_tamo_necesario / 1000) * costo_ton_tamo)
                
                consumo_paca_dia = peso_promedio * 0.03
                total_paca_necesaria = consumo_paca_dia * num_animales * dias_periodo
                costo_total_tradicional = (total_paca_necesaria / 1000) * costo_ton_paca
                
                ahorro_generado = costo_total_tradicional - costo_total_resiliencia
                porcentaje_ahorro = (ahorro_generado / costo_total_tradicional) * 100 if costo_total_tradicional > 0 else 0
                
                st.markdown("##### 📈 Proyección de Ahorro Operativo")
                col_res1, col_res2, col_res3 = st.columns(3)
                col_res1.metric("Inversión Dieta Tradicional", f"${costo_total_tradicional:,.2f}", "Compra externa", delta_color="inverse")
                col_res2.metric("Inversión Nopal + Tamo", f"${costo_total_resiliencia:,.2f}", "Aprovechamiento local", delta_color="off")
                col_res3.metric("Capital Salvado (Ahorro)", f"${ahorro_generado:,.2f}", f"{porcentaje_ahorro:.1f}% reducción de costos")

        # MODULO AZOLLA
        elif "Azolla" in tech_p1:
            st.markdown("### 🌱 Cultivo Rústico de Azolla")
            st.caption("📍 Origen de validación: Sistemas intensivos de pequeña escala en India y Asia de bajos recursos")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "MUY BAJO", "Estructuras rústicas de lona", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "MEDIO", "Adquisición de cepa madre por canales comerciales", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "MEDIA", "Requiere monitoreo diario de calidad de agua", delta_color="off")
            
            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Calculadora de Área de Cultivo"])
            
            with tab_info:
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Sustitución parcial de fuentes de proteína comerciales caras (Alfalfa, Pasta de Soya).
                        * Suplementación proteica en ganado lechero estabulado o semi-estabulado.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * No permitir que la temperatura del agua exceda los 38°C; genera muerte térmica del helecho.
                        * Mantener un control estricto de la carga orgánica (estiércol utilizado como fertilizante) para evitar procesos de eutrofización y descomposición anaeróbica de la pileta.
                    """)
                    
                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("1. Excavación y nivelación de fosas de 2x2 metros. 2. Colocación de película plástica impermeable. 3. Incorporación de suelo franco y fuente de fósforo/estiércol diluido. 4. Cosecha del 30% de la biomasa cada 24 horas.")

            with tab_receta:
                st.markdown("#### 🧮 Dimensionamiento de Módulos Acuáticos")
                st.write("Determine el área de piletas requerida para su lote y evalúe la viabilidad económica:")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    num_vacas = st.number_input("Animales a suplementar:", min_value=1, value=20, step=1)
                with col_c2:
                    consumo_diario_azolla = st.number_input("Consumo Azolla Fresca (kg/animal/día):", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
                with col_c3:
                    rendimiento_m2 = st.number_input("Rendimiento estimado (kg/m²/día):", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
                
                produccion_diaria_requerida = num_vacas * consumo_diario_azolla
                area_necesaria_m2 = produccion_diaria_requerida / rendimiento_m2
                
                st.subheader("📐 Requerimientos de Infraestructura")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.info(f"💧 **Área Activa de Cultivo:** {area_necesaria_m2:.1f} m²\n\n*Equivalente a {int(area_necesaria_m2/4) + 1} piletas estándar de 2x2 metros.*")
                with col_r2:
                    st.success(f"🌿 **Producción Diaria de Biomasa:** {produccion_diaria_requerida:.1f} kg frescos.")
                    
                st.divider()
                
                # CALCULADORA ROI FINANCIERO AZOLLA
                st.markdown("#### 💵 Impacto Financiero y Sustitución de Proteína")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    costo_kg_azolla = st.number_input("Costo operativo Azolla (kg fresco) [$]:", min_value=0.1, value=0.50, step=0.1, help="Considera agua, mano de obra y fertilizante.")
                with col_f2:
                    costo_kg_comercial = st.number_input("Costo Suplemento Comercial Sustituido (kg) [$]:", min_value=1.0, value=6.0, step=0.5, help="Costo del concentrado proteico equivalente.")
                
                gasto_diario_azolla = produccion_diaria_requerida * costo_kg_azolla
                gasto_diario_comercial = produccion_diaria_requerida * costo_kg_comercial
                ahorro_diario_azolla = gasto_diario_comercial - gasto_diario_azolla
                ahorro_anual_azolla = ahorro_diario_azolla * 365
                
                st.markdown("##### 📈 Proyección de Ahorro Anualizado")
                col_res1, col_res2, col_res3 = st.columns(3)
                col_res1.metric("Gasto Anual Comercial", f"${(gasto_diario_comercial * 365):,.2f}", delta_color="inverse")
                col_res2.metric("Gasto Anual Azolla", f"${(gasto_diario_azolla * 365):,.2f}", delta_color="off")
                col_res3.metric("Ahorro Neto Anualizado", f"${ahorro_anual_azolla:,.2f}", "Retención de flujo de caja")

        # MODULO SILO DE TAMO
        elif "Silo de Tamo" in tech_p1:
            st.markdown("### 🌾 Enriquecimiento de Esquilmos (Silo de Tamo)")
            st.caption("📍 Origen de validación: Sistemas de optimización de rastrojos a nivel global")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "BAJO", "Aprovechamiento de subproductos", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "ALTO", "Insumos base disponibles", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "ALTA", "Requiere precisión en dosificación", delta_color="inverse")
            
            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Calculadora de Enriquecimiento y ROI"])
            
            with tab_info:
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Conversión de forrajes de muy baja calidad (paja, rastrojo, tamo) en alimento de mantenimiento.
                        * Reducción de costos de alimentación invernal o en estiaje severo.
                        * Incremento de digestibilidad y proteína cruda en biomasa seca.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS (CRÍTICO):**
                        * **INTOXICACIÓN POR UREA:** Una mala disolución o aplicación heterogénea causará concentración de nitrógeno letal para el bovino.
                        * **BOTULISMO Y HONGOS:** Una compactación deficiente o ruptura del sello plástico (entrada de oxígeno) pudrirá el silo. Desechar cualquier capa negra o con moho.
                    """)
                    
                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Preparación:** Picar el rastrojo o tamo a un tamaño aproximado de 5 cm.
                    2. **Mezcla Líquida:** Disolver perfectamente la urea y la melaza en el agua estipulada. No deben quedar grumos ni residuos sólidos.
                    3. **Estratificación:** Extender el tamo en capas de 20 cm sobre una superficie limpia o trinchera.
                    4. **Asperjado y Compactado:** Rociar la mezcla líquida uniformemente sobre cada capa y compactar (con tractor o rodillo) para expulsar el aire.
                    5. **Sellado Anaeróbico:** Cubrir herméticamente con lona plástica y sellar bordes con tierra. Fermentar por un mínimo de 21 días antes de abrir.
                """)

            with tab_receta:
                st.markdown("#### 🧮 Dosificación Estructural de Amonificación")
                st.write("Determine los volúmenes de formulación requeridos para su inventario:")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    num_vacas_silo = st.number_input("Número de animales:", min_value=1, value=50, step=1, key="num_vacas_silo")
                with col_c2:
                    peso_promedio_silo = st.number_input("Peso vivo promedio (kg):", min_value=50, value=400, step=10, key="peso_silo")
                with col_c3:
                    dias_silo = st.number_input("Días de contingencia a cubrir:", min_value=1, value=60, step=5, key="dias_silo")
                
                consumo_ms_dia = peso_promedio_silo * 0.025
                total_tamo_base = consumo_ms_dia * num_vacas_silo * dias_silo
                
                factor_ton = total_tamo_base / 1000
                total_urea = factor_ton * 50
                total_melaza = factor_ton * 100
                total_agua = factor_ton * 300
                
                st.subheader("📊 Formulación Exacta del Silo")
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("🌾 Tamo/Rastrojo Seco", f"{total_tamo_base:,.1f} kg")
                col_r2.metric("🧪 Urea Agrícola/Pecuaria", f"{total_urea:,.1f} kg")
                col_r3.metric("🍯 Melaza y 💧 Agua", f"{total_melaza:,.1f} kg / {total_agua:,.1f} L")
                
                st.divider()
                
                # CALCULADORA ROI FINANCIERO SILO
                st.markdown("#### 💵 Impacto Financiero y Retorno Operativo")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    costo_tamo_base = st.number_input("Costo Tamo Seco (Ton) [$]:", min_value=100, value=1200, step=100, key="costo_tamo_silo_unico")
                    costo_urea = st.number_input("Costo Urea (kg) [$]:", min_value=1, value=12, step=1, key="costo_urea_silo_unico")
                    costo_melaza = st.number_input("Costo Melaza (kg) [$]:", min_value=1, value=6, step=1, key="costo_melaza_silo_unico")
                with col_f2:
                    costo_paca_comercial = st.number_input("Costo Paca Calidad Media (Ton) [$]:", min_value=1000, value=4500, step=100, key="costo_paca_silo_unico")
                
                costo_total_insumos_silo = (factor_ton * costo_tamo_base) + (total_urea * costo_urea) + (total_melaza * costo_melaza)
                costo_total_paca = factor_ton * costo_paca_comercial
                
                ahorro_silo = costo_total_paca - costo_total_insumos_silo
                porcentaje_ahorro_silo = (ahorro_silo / costo_total_paca) * 100 if costo_total_paca > 0 else 0
                
                st.markdown("##### 📈 Proyección de Ahorro en Alimentación Base")
                col_res1, col_res2, col_res3 = st.columns(3)
                col_res1.metric("Costo Equivalente Pacas", f"${costo_total_paca:,.2f}", delta_color="inverse")
                col_res2.metric("Costo Producción Silo", f"${costo_total_insumos_silo:,.2f}", delta_color="off")
                col_res3.metric("Capital Salvado", f"${ahorro_silo:,.2f}", f"{porcentaje_ahorro_silo:.1f}% de reducción")

    # 🦠 PILAR 2: SUELO Y MICROBIOLOGÍA
    elif "Pilar 2" in pilar_seleccionado:
        st.subheader("🦠 Regeneración Biológica del Suelo y Control Sanitario Natural")
        tech_p2 = st.radio("Seleccione la Tecnología Operativa:", ["🌳 Sistemas Silvopastoriles Intensivos (SSPi)", "🐄 Efecto Boma (Corrales Móviles)"], horizontal=True)
        st.divider()

        # MODULO SSPI
        if "Silvopastoriles" in tech_p2:
            st.markdown("### 🌳 Sistemas Silvopastoriles Intensivos (SSPi)")
            st.caption("📍 Origen de validación: Modelos tropicales y subtropicales de alta densidad")

            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "ALTO", "Inversión inicial en siembra", delta_color="inverse")
            col_v2.metric("🇲🇽 Acceso en México", "ALTO", "Semillas endémicas locales", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "MEDIA", "Requiere descansos estrictos", delta_color="off")

            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Proyección de Carga Animal"])

            with tab_info:
                st.markdown("#### 📖 Concepto Técnico")
                st.write("Integración de arbustos forrajeros en hileras dentro de los potreros. Triplica la biomasa comestible por metro cuadrado (crecimiento vertical) y provee sombra para confort animal.")
                
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Incremento de carga animal por hectárea sin uso de fertilizantes químicos.
                        * Mitigación de estrés calórico en el ganado.
                        * Fijación biológica de nitrógeno en suelos degradados.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * **TIEMPO DE ESTABLECIMIENTO:** No introducir ganado hasta que los arbustos alcancen 1.5 metros de altura (aprox. 6 a 8 meses).
                        * **TOXICIDAD:** Especies como Leucaena requieren un periodo de adaptación paulatina para la flora ruminal.
                    """)

                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Preparación de suelo:** Subsoleo y trazo de surcos siguiendo curvas de nivel.
                    2. **Siembra:** Hileras de arbustos separadas a 1.5 - 2.0 metros, intercaladas con pasto.
                    3. **Establecimiento:** Exclusión total de animales por 6-8 meses.
                    4. **Pastoreo:** Ramoneo intensivo por periodos cortos (12-24 horas) y descansos largos (40-60 días).
                """)

            with tab_receta:
                st.markdown("#### 🧮 Calculadora de Expansión del Rancho")
                st.write("Proyecte el incremento de capacidad instalada sin adquirir nuevas tierras:")

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    hectareas_disponibles = st.number_input("Hectáreas del potrero a sembrar:", min_value=1.0, value=10.0, step=1.0)
                    carga_actual = st.number_input("Carga animal actual (Vacas/Hectárea):", min_value=0.1, value=1.0, step=0.1)
                with col_c2:
                    multiplicador_sspi = st.slider("Multiplicador de biomasa esperado:", min_value=1.5, max_value=5.0, value=3.0, step=0.5)
                    valor_vaca_promedio = st.number_input("Valor comercial promedio por vaca ($):", min_value=5000, value=25000, step=1000)

                carga_proyectada = carga_actual * multiplicador_sspi
                vacas_actuales_totales = hectareas_disponibles * carga_actual
                vacas_nuevas_totales = hectareas_disponibles * carga_proyectada
                incremento_vacas = vacas_nuevas_totales - vacas_actuales_totales

                valor_capital_adicional = incremento_vacas * valor_vaca_promedio

                st.subheader("📊 Nuevo Límite Biológico del Rancho")
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Carga Actual (Total)", f"{vacas_actuales_totales:.0f} Cabezas")
                col_r2.metric("Nueva Carga SSPi", f"{vacas_nuevas_totales:.0f} Cabezas", f"+{incremento_vacas:.0f} espacios nuevos")
                col_r3.metric("Densidad Operativa", f"{carga_proyectada:.1f} Vacas/Ha")

                st.divider()
                st.markdown("##### 💵 Valorización de Activos Biológicos")
                st.metric("Incremento de Capital Soportado", f"${valor_capital_adicional:,.2f} MXN", "Capacidad extra del rancho valorizada en ganado")

        # MODULO EFECTO BOMA
        elif "Boma" in tech_p2:
            st.markdown("### 🐄 Efecto Boma (Corrales Móviles Nocturnos)")
            st.caption("📍 Origen de validación: Sabanas africanas (Manejo Holístico) y tierras áridas")

            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "MUY BAJO", "Costo de hilo eléctrico móvil", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "INMEDIATO", "Cero insumos externos", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "ALTA", "Exige movimiento diario", delta_color="inverse")

            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Ingeniería de Corral y Fertilizante"])

            with tab_info:
                st.markdown("#### 📖 Concepto Operativo")
                st.write("Confinamiento nocturno de alta densidad utilizando cercos móviles sobre áreas de suelo degradado. El impacto físico de las pezuñas rompe la costra del suelo, mientras que la concentración de excretas inyecta fertilidad biológica masiva.")
                
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Rehabilitación de zonas severamente degradadas o desnudas.
                        * Incorporación masiva de materia orgánica a costo cero.
                        * Protección contra depredadores nocturnos.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * **ZONAS INUNDABLES:** Evitar en temporada de lluvias intensas. El lodo profundo causa afecciones podales graves.
                        * **ESTANCIA PROLONGADA:** Prohibido dejar a los animales más de 12 horas en el mismo polígono.
                    """)

                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Selección del sitio:** Identificar el parche de tierra más estéril del potrero.
                    2. **Instalación:** Armar corral perimetral calculando 3 m² por Unidad Animal.
                    3. **Encierro:** Introducir al hato al caer la tarde.
                    4. **Rotación:** Al amanecer, abrir el corral, sacar al ganado a pastorear y mover la estructura.
                """)

            with tab_receta:
                st.markdown("#### 🧮 Dimensionamiento Físico y Químico")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    num_vacas_boma = st.number_input("Número de cabezas a confinar:", min_value=10, value=100, step=10)
                with col_c2:
                    peso_promedio_boma = st.number_input("Peso promedio por animal (kg):", min_value=100, value=400, step=10)

                peso_total_hato = num_vacas_boma * peso_promedio_boma
                ugm_totales = peso_total_hato / 500
                area_boma_m2 = ugm_totales * 3.0
                perimetro_metros = 4 * (area_boma_m2 ** 0.5)

                st.subheader("📐 Especificaciones Estructurales")
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("Área Requerida", f"{area_boma_m2:.1f} m²", "Confinamiento de alta densidad")
                col_r2.metric("Perímetro de Cerco", f"{perimetro_metros:.1f} metros lineales", "Diseño cuadrangular")

                st.divider()

                st.markdown("##### 💵 Ahorro Equivalente en Agroquímicos")
                
                excretas_frescas_noche = (peso_total_hato * 0.08) / 2
                nitrogeno_puro_kg = excretas_frescas_noche * 0.005 
                urea_equivalente_kg = nitrogeno_puro_kg * 2.17 

                costo_urea_kg = st.number_input("Precio de la Urea Química ($/kg):", min_value=1.0, value=15.0, step=1.0, key="costo_urea_boma")
                ahorro_fertilizante_diario = urea_equivalente_kg * costo_urea_kg

                col_f1, col_f2 = st.columns(2)
                col_f1.metric("Estiércol y Orina", f"{excretas_frescas_noche:,.1f} kg / noche")
                col_f2.metric("Ahorro Operativo", f"${ahorro_fertilizante_diario:,.2f} / noche", f"Equivalente a {urea_equivalente_kg:.1f} kg de Urea")



                st.markdown("##### 💵 Ahorro Equivalente en Agroquímicos")
                
                excretas_frescas_noche = (peso_total_hato * 0.08) / 2
                nitrogeno_puro_kg = excretas_frescas_noche * 0.005 
                urea_equivalente_kg = nitrogeno_puro_kg * 2.17 

                costo_urea_kg = st.number_input("Precio de la Urea Química ($/kg):", min_value=1.0, value=15.0, step=1.0, key="costo_urea_boma")
                ahorro_fertilizante_diario = urea_equivalente_kg * costo_urea_kg

                col_f1, col_f2 = st.columns(2)
                col_f1.metric("Estiércol y Orina", f"{excretas_frescas_noche:,.1f} kg / noche")
                col_f2.metric("Ahorro Operativo", f"${ahorro_fertilizante_diario:,.2f} / noche", f"Equivalente a {urea_equivalente_kg:.1f} kg de Urea")

    # 📡 PILAR 3: ESCALABILIDAD Y PROCESOS
    elif "Pilar 3" in pilar_seleccionado:
        st.subheader("📡 Escalabilidad y Manejo Dinámico (Procesos y Tecnología)")
        tech_p3 = st.radio("Seleccione la Tecnología Operativa:", ["🛰️ Cercos Virtuales (Collares GPS)", "📊 Pastoreo Holístico (Aforo Diario)"], horizontal=True)
        st.divider()

        # MODULO CERCOS VIRTUALES
        if "Cercos" in tech_p3:
            st.markdown("### 🛰️ Cercos Virtuales (Collares GPS y Telemetría)")
            st.caption("📍 Origen de validación: Estaciones experimentales y ganadería de precisión")

            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "ALTO", "Adquisición de Hardware", delta_color="inverse")
            col_v2.metric("🇲🇽 Acceso en México", "MEDIO", "Importación tecnológica", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "ALTA", "Uso de software georreferenciado", delta_color="inverse")

            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Análisis de Capitalización (ROI)"])

            with tab_info:
                st.markdown("#### 📖 Concepto Operativo")
                st.write("Sustitución de barreras físicas por dispositivos de control individual (collares). Emiten estímulos auditivos y sensoriales para confinar al ganado dentro de polígonos virtuales trazados en plataformas digitales.")
                
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Implementación de rotación ultra-intensiva sin inversión en alambres.
                        * Exclusión estricta de zonas ecológicas (cuerpos de agua, reforestaciones).
                        * Mitigación de costos de nómina por patrullaje y reparación de cercos.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * **TOPOGRAFÍA:** Inoperable en zonas con nula cobertura de red celular o señal satelital deficiente.
                        * **PERÍMETROS EXTERNOS:** El sistema NO exime la necesidad de un cerco físico exterior robusto para prevenir robos o invasión a carreteras.
                    """)

                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Equipamiento:** Colocación del hardware en el 100% del hato a controlar.
                    2. **Calibración:** Periodo de entrenamiento (3-5 días) en potrero físico cerrado para asociación neurológica del estímulo.
                    3. **Programación:** Trazo diario de polígonos de pastoreo mediante aplicación móvil o web.
                    4. **Telemetría:** Monitoreo remoto de mapas de calor, niveles de batería y alertas de fuga.
                """)

            with tab_receta:
                st.markdown("#### 💵 Impacto Financiero: Tecnología vs Infraestructura Tradicional")
                st.write("Proyección comparativa del costo de hardware versus el levantamiento de cercos físicos divisores.")

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    km_cerco_evitados = st.number_input("Kilómetros de cerco físico a sustituir:", min_value=1.0, value=10.0, step=1.0)
                    costo_km_cerco = st.number_input("Costo promedio de 1 km de cerco ($):", min_value=10000.0, value=35000.0, step=5000.0)
                with col_c2:
                    cabezas_a_equipar = st.number_input("Número de cabezas (collares requeridos):", min_value=1, value=50, step=5)
                    costo_collar_unitario = st.number_input("Costo unitario por collar GPS ($):", min_value=1000.0, value=3000.0, step=500.0)

                inversion_cerco_fisico = km_cerco_evitados * costo_km_cerco
                inversion_collares = cabezas_a_equipar * costo_collar_unitario
                ahorro_infraestructura = inversion_cerco_fisico - inversion_collares
                
                st.subheader("📊 Diagnóstico de Retorno de Inversión")
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Gasto en Cerco Físico", f"${inversion_cerco_fisico:,.2f}", delta_color="inverse")
                col_r2.metric("Inversión en Collares", f"${inversion_collares:,.2f}", delta_color="off")
                
                if ahorro_infraestructura > 0:
                    col_r3.metric("Capital a Favor", f"${ahorro_infraestructura:,.2f}", "Punto de equilibrio superado")
                else:
                    col_r3.metric("Déficit de Inversión", f"${ahorro_infraestructura:,.2f}", "Costo de hardware excede infraestructura", delta_color="inverse")

        # MODULO PASTOREO HOLISTICO
        elif "Pastoreo" in tech_p3:
            st.markdown("### 📊 Pastoreo Holístico (Gestión de Aforos)")
            st.info("**¿Qué es?** En lugar de dejar a las vacas sueltas en un potrero gigante por un mes, divides el potrero en secciones pequeñas. Las vacas entran, comen todo parejo por 1 o 2 días, y las mueves a la siguiente sección. **Resultado:** El pasto recibe descansos largos para crecer más fuerte y evitas que el rancho se llene de maleza.")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "BAJO", "Uso de recursos existentes", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "INMEDIATO", "Metodología de rotación", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "ALTA", "Exige medir pasto y mover ganado", delta_color="inverse")

            tab_info, tab_receta = st.tabs(["📋 Manual Operativo", "🧮 Calculadora de Días de Ocupación"])

            with tab_info:
                st.error("🛑 **REGLA DE ORO:** El tiempo de ocupación en una parcela NUNCA debe superar los 3 días. Si las dejas más tiempo, la vaca se comerá el rebrote nuevo de la planta y la matará de raíz.")

                st.markdown("#### 🛠️ Pasos de Operación")
                st.write("1. **Medir (Aforo):** Corta un cuadrado de 1x1 metro de tu pasto y pésalo para saber cuánta comida hay.\n2. **Calcular:** Usa la pestaña de al lado para saber cuántos días les durará esa comida.\n3. **Mover:** Abre la puerta a la siguiente parcela antes de que el pasto quede a ras de suelo.\n4. **Descansar:** No regreses a las vacas a esa primera parcela hasta que el pasto vuelva a estar alto y maduro.")

            with tab_receta:
                st.markdown("#### 🧮 Calculadora de Capacidad de Carga")
                st.write("Calcula exactamente cuántos días puedes dejar a tu lote en un potrero sin destruir el pasto:")

                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    st.markdown("**1. Tu Ganado (Demanda)**")
                    peso_promedio_ph = st.number_input("Peso promedio por vaca (kg):", min_value=100, value=400, step=10)
                    cabezas_ph = st.number_input("Número de cabezas en el lote:", min_value=10, value=100, step=5)
                with col_c2:
                    st.markdown("**2. Tu Pasto (Oferta)**")
                    aforo_m2 = st.number_input("¿Cuánto pesa 1m² de tu pasto? (kg):", min_value=0.1, value=1.5, step=0.1, help="Corta 1 metro cuadrado de pasto a ras de suelo y pésalo.")
                    hectareas_potrero = st.number_input("Tamaño del potrero (Hectáreas):", min_value=1.0, value=2.0, step=0.5)
                with col_c3:
                    st.markdown("**3. Eficiencia**")
                    porcentaje_aprovechamiento = st.slider("Desperdicio (%):", min_value=30, max_value=80, value=50, help="El ganado pisotea y ensucia pasto. 50% significa que solo aprovechan la mitad de la comida.")

                consumo_diario_hato = cabezas_ph * (peso_promedio_ph * 0.10) 
                forraje_total_verde = (aforo_m2 * 10000) * hectareas_potrero
                forraje_util = forraje_total_verde * (porcentaje_aprovechamiento / 100)
                
                dias_ocupacion = forraje_util / consumo_diario_hato if consumo_diario_hato > 0 else 0

                st.divider()
                st.subheader("📊 Veredicto de Rotación")
                col_r1, col_r2, col_r3 = st.columns(3)
                
                col_r1.metric("Comida Real Disponible", f"{forraje_util / 1000:,.1f} Toneladas", "Ya descontando el pasto pisoteado")
                col_r2.metric("Consumo del Lote", f"{consumo_diario_hato:,.1f} kg / día", "Lo que tragan todos juntos en 24 hrs")
                
                if dias_ocupacion > 3:
                    col_r3.metric("Límite de Ocupación", f"{dias_ocupacion:.1f} Días", "⚠️ Demasiado tiempo. Subdivide tu potrero.", delta_color="inverse")
                else:
                    col_r3.metric("Límite de Ocupación", f"{dias_ocupacion:.1f} Días", "✅ Rango perfecto de pastoreo.", delta_color="off")    