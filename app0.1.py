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

#CONFIGURACIÓN
st.set_page_config(page_title="AgroIA v3.1", page_icon="🐄", layout="wide")
st.title("🌾 Sistema de Inteligencia Agropecuaria v3.1")

#CARGAR DATOS
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
def registrar_bitacora(accion, detalle):
    try:
        supabase.table("bitacora").insert({
            "accion": accion,
            "detalle": detalle
        }).execute()
    except Exception as e:
        st.error(f"Error al guardar en la Caja Negra: {e}")

#MENÚ LATERAL
st.sidebar.header("⚙️ Panel de Control")
opcion = st.sidebar.radio(
    "Seleccione un Módulo:",
    (
        "1. Inventario de Insumos", 
        "2. Diseñar Perfil Animal", 
        "3. Laboratorio de Mezclas", 
        "4. Proyección Financiera", 
        "5. Caja Negra (Bitácora)",
        "6. Motor IA"
    )
)

#MÓDULO 1: INVENTARIO DE INSUMOS
if "1." in opcion:
    st.header("📦 Control de Bodega y Precios")
    
    st.subheader("📊 Estado Actual del Inventario")
    
    inventario_visual = []
    for insumo, datos in base_datos.items():
        stock = datos.get("stock_kg", 0)
        precio = datos.get("costo_kg", 0)
        
        if stock <= 500:
            estatus = "🔴 CRÍTICO (Comprar)"
        elif stock <= 2000:
            estatus = "🟡 PRECAUCIÓN"
        else:
            estatus = "🟢 ÓPTIMO"
            
        inventario_visual.append({
            "Insumo": insumo.upper(),
            "Stock en Bodega (kg)": stock,
            "Costo Actual ($/kg)": precio,
            "Estado": estatus
        })
        
    df_inventario = pd.DataFrame(inventario_visual)
    st.dataframe(df_inventario, use_container_width=True)
    
    #ACTUALIZAR INVENTARIO O PRECIOS
    st.divider()
    st.subheader("🛒 Ingresar Mercancía o Cambiar Precios")
    st.markdown("¿Llegó el camión o subió el precio? Actualízalo aquí sin tocar el código.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        insumo_edit = st.selectbox("Selecciona el Insumo:", list(base_datos.keys()))
    with col2:
        # Sumar o restar kilos
        nuevo_stock = st.number_input("Agregar/Quitar Kilos:", value=0.0, step=50.0)
        st.caption(f"Stock actual: {base_datos[insumo_edit].get('stock_kg', 0)} kg")
    with col3:
        # Modificar el precio
        nuevo_precio = st.number_input("Nuevo Precio ($/kg):", value=float(base_datos[insumo_edit].get("costo_kg", 0)), step=0.1)
        
    if st.button("💾 Guardar Cambios en Bodega"):
        base_datos[insumo_edit]["stock_kg"] += nuevo_stock
        base_datos[insumo_edit]["costo_kg"] = nuevo_precio
        
        # GUARDAR EN SUPABASE
        supabase.table("inventario").update({
            "stock_kg": float(base_datos[insumo_edit]["stock_kg"]),
            "costo_kg": float(base_datos[insumo_edit]["costo_kg"])
        }).eq("insumo", insumo_edit).execute()
        
        registrar_bitacora("Inventario Manual", f"Se actualizó {insumo_edit.upper()}: {nuevo_stock} kg agregados/quitados. Nuevo precio: ${nuevo_precio}")
            
        st.success(f"✅ ¡{insumo_edit.upper()} actualizado correctamente!")
        st.rerun() 

    st.divider()
    st.subheader("🌐 Radar Satelital: Bolsa de Valores")
    st.markdown("Cotiza el precio internacional del **Maíz** en tiempo real (ajustado al tipo de cambio USD/MXN).")
    
    if st.button("📡 Sincronizar Precio del Maíz con Chicago"):
        with st.spinner("Hackeando la matriz financiera..."):
            try:
                # 1. Traer tipo de cambio Dólar a Peso (USD/MXN)
                usd_mxn = yf.Ticker("MXN=X")
                precio_dolar = usd_mxn.fast_info['lastPrice']
                
                # 2. Traer precio del Maíz (Futuros de Chicago: ZC=F) 
                maiz_ticker = yf.Ticker("ZC=F")
                precio_centavos_bushel = maiz_ticker.fast_info['lastPrice']
                
                # 3 Matemáticas de conversión (1 Bushel de Maíz = 25.401 kg)
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

elif opcion == "2. Diseñar Perfil Animal":
    st.header("🧬 Configuración de Inteligencia Genética")
    
    with st.form("perfil_animal"):
        col1, col2 = st.columns(2)
        
        with col1:
            raza_sel = st.selectbox("1. Seleccione la Raza:", 
                                   ["brahman", "nelore", "angus", "hereford", "brangus", "simbrah", "holstein"])
            genero = st.radio("2. Género:", ["Macho", "Hembra"], horizontal=True)
            proposito = st.selectbox("3. Propósito:", ["Carne", "Leche", "Semental", "Doble Propósito"])
            
        with col2:
            edad = st.number_input("4. Edad (meses):", min_value=1, max_value=200, value=5)
            peso = st.number_input("5. Peso Vivo Estimado (kg):", min_value=30, max_value=1500, value=180)
            clima = st.slider("6. Temperatura Ambiente (°C):", 0, 50, 32)
            
        enviado = st.form_submit_button("🔥 GUARDAR Y ANALIZAR PERFIL")

    if enviado:
        #INTELIGENCIA VETERINARIA
        dosis_desparasitante = peso / 50
        costo_desparasitante = dosis_desparasitante * 2.5
        
        costo_vacunas_base = 45.0 
        costo_salud_total = costo_desparasitante + costo_vacunas_base

        st.session_state['perfil'] = {
            "raza": raza_sel,
            "genero": genero.lower(),
            "edad": edad,
            "proposito": proposito.lower(),
            "clima": clima,
            "peso": peso,
            "costo_salud": costo_salud_total  
        }
        st.success(f"✅ Perfil de {raza_sel.upper()} guardado en memoria.")

        st.divider()
        st.subheader("💉 Protocolo Sanitario de Ingreso (Sugerido)")
        st.markdown(f"**Recomendación para un {raza_sel.title()} de {peso} kg:**")
        
        med1, med2, med3 = st.columns(3)
        med1.metric("Desparasitante (Ivermectina 1%)", f"{dosis_desparasitante:.1f} ml")
        med2.metric("Vacunas Base", "Rabia + Clostridios + ADE")
        med3.metric("Costo Médico Inicial", f"${costo_salud_total:.2f} MXN")
        
        st.caption("💡 *Nota: Un animal sano asimila mejor la dieta. Este costo de salud ya se guardó para tu proyección financiera.*")

        if raza_sel in ["angus", "hereford", "holstein"] and clima > 30:
            st.error(f"⚠️ ALERTA DE ADAPTABILIDAD: El {raza_sel.upper()} es de clima templado. A {clima}°C sufrirá estrés calórico severo.")
        elif clima > 35:
            st.warning("⚠️ ALERTA: Temperatura extrema. Se recomienda sombra y suplementación energética.")

# MODULO 3
elif opcion == "3. Laboratorio de Mezclas":
    st.header("🧪 Laboratorio de Mezclas y Riesgos")
    
    if 'perfil' not in st.session_state:
        st.warning("⚠️ Primero debe configurar el animal en el Módulo 2.")
    else:
        st.info(f"Analizando dieta para: {st.session_state['perfil']['raza'].upper()} ({st.session_state['perfil']['peso']} kg)")
        #BUSCADOR INTELIGENTE
        st.subheader("🔎 Buscador Filtrado")
        
        filtro = st.radio(
            "Filtrar ingredientes por aporte principal:",
            ("Todos", "Alta Proteína (>20%)", "Alta Energía (>2.8 Mcal)", "Alta Fibra (>20%)"),
            horizontal=True
        )
        
        lista_filtrada = []
        for insumo, datos in base_datos.items():
            if filtro == "Todos":
                lista_filtrada.append(insumo)
            elif "Proteína" in filtro and datos.get("proteina_pct", 0) >= 20.0:
                lista_filtrada.append(insumo)
            elif "Energía" in filtro and datos.get("energia_mcal", 0) >= 2.8:
                lista_filtrada.append(insumo)
            elif "Fibra" in filtro and datos.get("fibra_pct", 0) >= 20.0:
                lista_filtrada.append(insumo)
        
        if not lista_filtrada:
            st.warning("No hay insumos en tu bodega que cumplan este filtro.")

        if "receta_guardada_ia" in st.session_state:
            st.success("🤖 Receta de la IA detectada en la nube.")
            if st.button("📥 Importar Receta a la Mesa de Trabajo", key="btn_importar_unica"):
                st.session_state["memoria_selector"] = st.session_state["receta_guardada_ia"]["ingredientes"]
                for ins, kg in st.session_state["receta_guardada_ia"]["kilos"].items():
                    st.session_state[f"kg_{ins}"] = kg
        seleccionados = st.multiselect("Seleccione los ingredientes a utilizar:", lista_filtrada, key="memoria_selector")
        
        if seleccionados:
            mezcla_final = []
            total_kilos_mezcla = 0
            
            cols = st.columns(len(seleccionados))
            for i, insumo in enumerate(seleccionados):
                with cols[i]:
                    kilos = st.number_input(f"Kg de {insumo}", min_value=0.0, step=1.0, key=f"kg_{insumo}")
                    mezcla_final.append({"nombre": insumo, "kilos": kilos, "datos": base_datos[insumo]})
                    total_kilos_mezcla += kilos
           #AUDITORÍA DE MEZCLA
            if st.button("🔬 AUDITAR MEZCLA"):
                if total_kilos_mezcla > 0:
                    prot_acum = sum((item["kilos"] * item["datos"]["proteina_pct"]) for item in mezcla_final) / total_kilos_mezcla
                    ener_acum = sum((item["kilos"] * item["datos"]["energia_mcal"]) for item in mezcla_final) / total_kilos_mezcla
                    fibr_acum = sum((item["kilos"] * item["datos"]["fibra_pct"]) for item in mezcla_final) / total_kilos_mezcla
                    costo_tot = sum((item["kilos"] * item["datos"]["costo_kg"]) for item in mezcla_final)
                    
                    st.session_state['mezcla'] = {
                        "proteina": prot_acum, "energia": ener_acum, "fibra": fibr_acum,
                        "costo_total": costo_tot, "total_kilos": total_kilos_mezcla,
                        "costo_kg": costo_tot / total_kilos_mezcla,
                        "detalle": mezcla_final
                    }
                    
                    st.success("✅ Auditoría completada")
                    
                    # MÉTRICAS PRINCIPALES
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Proteína Cruda", f"{prot_acum:.2f}%")
                    c2.metric("Energía Metab.", f"{ener_acum:.2f} Mcal")
                    c3.metric("Fibra (FDN)", f"{fibr_acum:.2f}%")

                    # DESGLOSE PROFUNDO DE NUTRIENTES
                    st.divider()
                    st.subheader("📊 Radiografía Detallada por Insumo")
                    
                    datos_desglose = []
                    for item in mezcla_final:
                        kg_ingrediente = item["kilos"]
                        pct_mezcla = (kg_ingrediente / total_kilos_mezcla) * 100
                        kg_proteina = kg_ingrediente * (item["datos"]["proteina_pct"] / 100)
                        
                        datos_desglose.append({
                            "Insumo": item["nombre"].upper(),
                            "Participación (%)": round(pct_mezcla, 2),
                            "Aporte Proteína (kg)": round(kg_proteina, 2),
                            "Costo en Mezcla ($)": round(kg_ingrediente * item["datos"]["costo_kg"], 2)
                        })
                    
                    df_desglose = pd.DataFrame(datos_desglose)
                    st.dataframe(df_desglose, use_container_width=True)
                    st.divider()
                    st.subheader("🥧 Distribución de la Dieta")
                    
                    col_graf1, col_graf2 = st.columns(2)
                    
                    with col_graf1:
                        fig1 = px.pie(
                            df_desglose, 
                            values='Participación (%)', 
                            names='Insumo', 
                            title='Composición Física de la Mezcla',
                            hole=0.4 
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                        
                    with col_graf2:
                        fig2 = px.pie(
                            df_desglose, 
                            values='Aporte Proteína (kg)', 
                            names='Insumo', 
                            title='Aporte de Proteína por Insumo',
                            hole=0.4
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                    # ALERTAS VETERINARIAS PREVENTIVAS
                    if prot_acum > 18.0:
                        st.warning("⚠️ RIESGO: Nivel de proteína muy alto. Podría causar estrés renal en el animal y desperdicio de dinero.")
                    elif fibr_acum < 10.0:
                        st.warning("⚠️ RIESGO: Fibra muy baja. Peligro inminente de acidosis ruminal.")
                else:
                    st.error("Agregue kilos a los ingredientes.")
                    
    # CORRECTOR DE TOLVA (PEARSON)
    st.divider()
    st.subheader("⚖️ Corrector de Mezcla (Cuadrado de Pearson)")
    st.markdown("Calcula cuánto ingrediente de 'refuerzo' añadir para corregir la proteína de una mezcla ya existente.")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        prot_actual = st.number_input("Proteína actual de la mezcla (%)", value=11.0, step=0.5)
        kilos_en_tolva = st.number_input("Kilos actuales en la revolvedora", value=1000, step=100)
    with col_p2:
        prot_objetivo = st.number_input("Proteína objetivo (%)", value=14.0, step=0.5)
        ing_refuerzo = st.selectbox("Selecciona ingrediente de refuerzo:", list(base_datos.keys()))
        prot_refuerzo = base_datos[ing_refuerzo]["proteina_pct"]

    if st.button("🧮 Calcular Corrección"):
        # Lógica del Cuadrado de Pearson
        if prot_objetivo <= prot_actual or prot_objetivo >= prot_refuerzo:
            st.error("Misión Imposible: La proteína objetivo debe estar ENTRE la actual y la del refuerzo.")
        else:
            # Partes del refuerzo = |Prot Objetivo - Prot Actual|
            # Partes de la mezcla = |Prot Refuerzo - Prot Objetivo|
            partes_refuerzo = abs(prot_objetivo - prot_actual)
            partes_mezcla = abs(prot_refuerzo - prot_objetivo)
            total_partes = partes_refuerzo + partes_mezcla
            
            # Kilos de refuerzo a añadir = (Kilos en tolva / Partes mezcla) * Partes refuerzo
            kilos_a_añadir = (kilos_en_tolva / partes_mezcla) * partes_refuerzo
            nuevo_total = kilos_en_tolva + kilos_a_añadir
            
            st.success(f"**Resultado:** Añade **{kilos_a_añadir:.2f} kg** de **{ing_refuerzo.upper()}**.")
            st.info(f"Tendrás un total de **{nuevo_total:.2f} kg** al **{prot_objetivo}%** de proteína.")
            
            registrar_bitacora("Corrección Pearson", f"Se corrigió tolva de {kilos_en_tolva}kg al {prot_objetivo}% usando {ing_refuerzo}.")

#MÓDULO 4: PROYECCIÓN FINANCIERA
elif opcion == "4. Proyección Financiera":
    st.header("📈 Centro de Control Financiero")
    
    if 'perfil' not in st.session_state or 'mezcla' not in st.session_state:
        st.error("⚠️ Datos incompletos. Configure Perfil (Módulo 2) y Mezcla (Módulo 3).")
    else:
        perf = st.session_state['perfil']
        mezc = st.session_state['mezcla']
        
        ganancia_est = 0.8 + ((mezc["proteina"] - 14.0) * 0.05)
        consumo_diario = perf["peso"] * 0.03
        costo_salud_amortizado = perf.get("costo_salud", 0) / 100
        costo_dia = consumo_diario * mezc["costo_kg"]
        costo_kg_carne = costo_dia / ganancia_est
        
        #INTELIGENCIA DE PRECIOS
        st.subheader("🦈 Inteligencia de Mercado")
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            precio_venta = st.number_input("Precio de Venta en Pie ($/kg):", min_value=10.0, value=55.0, step=1.0)
        
        margen_por_kilo = precio_venta - costo_kg_carne
        ganancia_neta_diaria = margen_por_kilo * ganancia_est
        
        with col_m2:
            st.metric("Costo de Producción", f"${costo_kg_carne:.2f}/kg")
            
        with col_m3:
            if margen_por_kilo > 0:
                st.metric("Margen de Utilidad", f"${margen_por_kilo:.2f}/kg", delta="Rentable")
            else:
                st.metric("Margen de Utilidad", f"${margen_por_kilo:.2f}/kg", delta="-Pérdida", delta_color="inverse")

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

        #BOTÓN DE CAJA NEGRA
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
    
#MÓDULO 5: CAJA NEGRA

elif opcion == "5. Caja Negra (Bitácora)":
    st.header("📓 Caja Negra: Historial de Movimientos")
    st.markdown("Auditoría en tiempo real de las operaciones del rancho.")
    
    try:
        respuesta = supabase.table("bitacora").select("*").order("fecha", desc=True).execute()
        
        if respuesta.data:
            df_bitacora = pd.DataFrame(respuesta.data)
            df_bitacora['fecha'] = pd.to_datetime(df_bitacora['fecha'])
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                # Gráfica de Pastel: Tipos de Acciones
                fig_pie = px.pie(df_bitacora, names='accion', title='📊 Distribución de Actividades',
                               hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_g2:
                # Gráfica de Barras: Actividad por día
                df_bitacora['dia'] = df_bitacora['fecha'].dt.date
                resumen_dia = df_bitacora.groupby('dia').size().reset_index(name='conteo')
                fig_bar = px.bar(resumen_dia, x='dia', y='conteo', title='📈 Intensidad de Operación',
                                labels={'dia': 'Fecha', 'conteo': 'Movimientos'},
                                color_discrete_sequence=['#00CC96'])
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.divider()
            
            df_bitacora['fecha_str'] = df_bitacora['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df_final = df_bitacora[['fecha_str', 'accion', 'detalle']]
            df_final.columns = ['Fecha y Hora', 'Tipo de Acción', 'Detalle del Movimiento']
            
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
        else:
            st.info("La bitácora está limpia. Aún no hay movimientos registrados.")
            
    except Exception as e:
        st.error(f"Error al leer la Caja Negra: {e}")
            

#MÓDULO 6: AUTO-FORMULACIÓN (IA)
elif opcion == "6. Motor IA":
    st.header("🤖 Motor de Optimización Lineal (IA)")
    st.markdown("Dile a la máquina qué nutrientes necesitas y ella calculará la receta **más barata posible** respetando los límites de salud del animal.")

    col1, col2 = st.columns(2)
    with col1:
        req_proteina = st.number_input("🎯 Objetivo de Proteína (%)", min_value=5.0, max_value=30.0, value=14.0, step=0.5)
    with col2:
        req_energia = st.number_input("⚡ Objetivo de Energía (Mcal)", min_value=1.0, max_value=4.0, value=2.5, step=0.1)

    if st.button("🧠 GENERAR FÓRMULA ÓPTIMA"):
        prob = pulp.LpProblem("Dieta_Barata", pulp.LpMinimize)
        insumos = list(base_datos.keys())
        x = pulp.LpVariable.dicts("Ingrediente", insumos, lowBound=0)

        # LA META: Minimizar costo total
        prob += pulp.lpSum([x[i] * base_datos[i]["costo_kg"] for i in insumos]), "Costo"

        # RESTRICCIONES 
        prob += pulp.lpSum([x[i] for i in insumos]) == 100, "Peso_100"
        prob += pulp.lpSum([x[i] * base_datos[i]["proteina_pct"] for i in insumos]) >= req_proteina * 100, "Req_Prot"
        prob += pulp.lpSum([x[i] * base_datos[i]["energia_mcal"] for i in insumos]) >= req_energia * 100, "Req_Ener"
        
        for i in insumos:
            if "max_pct" in base_datos[i]:
                prob += x[i] <= base_datos[i]["max_pct"], f"Max_{i}"

        prob.solve()

        if pulp.LpStatus[prob.status] == "Optimal":
            # GUARDAR RESULTADO EN MEMORIA 
            resultados = []
            costo_cien_kg = 0
            for i in insumos:
                kilos_sugeridos = x[i].varValue
                if kilos_sugeridos > 0.01:
                    costo_ing = kilos_sugeridos * base_datos[i]["costo_kg"]
                    costo_cien_kg += costo_ing
                    resultados.append({
                        "Insumo": i.upper(),
                        "Kilos a mezclar (por cada 100kg)": round(kilos_sugeridos, 2),
                        "Costo en la dieta ($)": round(costo_ing, 2)
                    })
            
            st.session_state['solucion_ia'] = {
                "df": pd.DataFrame(resultados),
                "costo_kg": costo_cien_kg / 100,
                "detalles_ia": {
                    "ingredientes": [i for i in insumos if x[i].varValue > 0.01],
                    "kilos": {i: float(x[i].varValue) for i in insumos if x[i].varValue > 0.01}
                }
            }
            st.balloons()
            registrar_bitacora("Motor IA", f"Fórmula generada. Costo proyectado: ${costo_cien_kg/100:.2f}/kg.")
        else:
            st.session_state['solucion_ia'] = None
            st.error("❌ Misión Imposible. La bodega no tiene ingredientes suficientes para esta meta.")

    # BLOQUE DE VISUALIZACIÓN 
    if 'solucion_ia' in st.session_state and st.session_state['solucion_ia'] is not None:
        sol = st.session_state['solucion_ia']
        
        st.success("✅ ¡Fórmula óptima encontrada!")
        st.title(f"💰 Costo final proyectado: ${sol['costo_kg']:.2f} MXN / kg")
        st.dataframe(sol['df'], use_container_width=True, hide_index=True)
        
        # PUENTE AL LABORATORIO 
        st.divider()
        if st.button("💾 Enviar Receta a Memoria de Mezclado"):
            st.session_state["receta_guardada_ia"] = sol['detalles_ia']
            st.info("📥 Receta enviada. Ve al Módulo 3 y pícale a 'Importar Receta IA'.")

        # ESCALADOR LOGÍSTICO
        st.divider()
        st.subheader("🚜 Escalador Logístico (Proyección de Compras)")
        c_lote1, c_lote2, c_lote3 = st.columns(3)
        with c_lote1: num_cabezas = st.number_input("Número de Animales", value=100, step=10)
        with c_lote2: consumo_cab = st.number_input("Consumo (kg/animal/día)", value=10.0, step=0.5)
        with c_lote3: dias_dieta = st.number_input("Días de Alimentación", value=30, step=5)
            
        if st.button("📦 Calcular Toneladas a Comprar", use_container_width=True):
            kilos_totales = num_cabezas * consumo_cab * dias_dieta
            ton_totales = kilos_totales / 1000
            st.success(f"**Requerimiento Total del Lote:** {ton_totales:,.1f} Toneladas.")
            
            df_compra = sol['df'].copy()
            df_compra["Toneladas a Pedir"] = (df_compra["Kilos a mezclar (por cada 100kg)"] / 100) * ton_totales
            df_compra["Toneladas a Pedir"] = df_compra["Toneladas a Pedir"].apply(lambda x: f"{x:,.2f} Ton")
            st.dataframe(df_compra[["Insumo", "Toneladas a Pedir"]], use_container_width=True, hide_index=True)
            registrar_bitacora("Cálculo Logístico", f"Proyección de {ton_totales:.1f} Ton para {num_cabezas} animales.")