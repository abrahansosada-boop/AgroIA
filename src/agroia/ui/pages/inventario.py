import streamlit as st
import pandas as pd
import yfinance as yf
import time
from agroia.repositories.inventory import (
    evaluar_alerta_dias, 
    evaluar_alerta_kilos, 
    procesar_movimiento_bodega, 
    convertir_precio_chicago
)

def renderizar_inventario(base_datos, supabase, registrar_bitacora, es_administrador):
    st.header("📦 Control de Bodega y Precios")
    
    st.subheader("📊 Estado Actual del Inventario")
    
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
        
        if "Días" in tipo_alerta:
            estatus = evaluar_alerta_dias(stock, consumo_diario, limite_critico)["estado"]
        else:
            estatus = evaluar_alerta_kilos(stock, limite_critico)
                
        inventario_visual.append({
            "Insumo": insumo.upper(),
            "Stock en Bodega (kg)": round(stock, 2),
            "Costo Actual ($/kg)": round(precio, 2),
            "Estado": estatus
        })
        
    df_inventario = pd.DataFrame(inventario_visual)
    if not es_administrador:
        if "Costo Actual ($/kg)" in df_inventario.columns:
            df_inventario = df_inventario.drop(columns=["Costo Actual ($/kg)"])        
    st.dataframe(df_inventario, use_container_width=True, hide_index=True)
    
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
        nuevo_precio = 0.0
        
        if "Ingreso" in tipo_movimiento:
            nuevo_precio = st.number_input("Nuevo precio de compra ($/kg)", value=float(base_datos[insumo_edit]["costo_kg"]), step=0.1)
        elif "Merma" in tipo_movimiento:
            causa_merma = st.selectbox("Causa de la pérdida:", ["Humedad/Lluvia", "Plagas (Ratones/Gorgojo)", "Accidente/Rotura", "Robo/Extravío"])
            perdida_calculada = kilos_mov * base_datos[insumo_edit]['costo_kg']
            st.warning(f"💸 Esto generará una pérdida auditada de **${perdida_calculada:,.2f} MXN**")

    if st.button("💾 Registrar Movimiento en Bóveda", use_container_width=True):
        stock_actual = base_datos[insumo_edit]["stock_kg"]
        precio_actual = base_datos[insumo_edit]["costo_kg"]
        
        res_mov = procesar_movimiento_bodega(stock_actual, precio_actual, kilos_mov, tipo_movimiento, nuevo_precio)
        
        if not res_mov["exito"]:
            st.error(f"⚠️ {res_mov['error']}")
        else:
            try:
                nuevo_stock = res_mov["nuevo_stock"]
                precio_final = res_mov["precio_final"]
                
                if "Ingreso" in tipo_movimiento:
                    tipo_accion, detalle = "Compra de Insumo", f"Ingreso de {kilos_mov}kg de {insumo_edit.upper()}. Nuevo precio: ${precio_final}"
                elif "Ajuste" in tipo_movimiento:
                    tipo_accion, detalle = "Ajuste de Bodega", f"Ajuste manual de {insumo_edit.upper()}: {kilos_mov}kg."
                else:
                    tipo_accion, detalle = "Merma Financiera", f"MERMA de {kilos_mov}kg de {insumo_edit.upper()} por {causa_merma}. Fuga: ${res_mov['perdida_dinero']:,.2f}"

                respuesta = supabase.table("inventario").update({
                    "stock_kg": float(nuevo_stock),
                    "costo_kg": float(precio_final)
                }).eq("insumo", insumo_edit).execute()

                if not respuesta.data:
                    st.error(f"❌ Falso positivo evitado: No se encontró la fila '{insumo_edit}' en la tabla de Supabase.")
                else:
                    base_datos[insumo_edit]["stock_kg"] = float(nuevo_stock)
                    base_datos[insumo_edit]["costo_kg"] = float(precio_final)
                    registrar_bitacora(tipo_accion, detalle)
                    st.success(f"✅ ¡Movimiento de {insumo_edit.upper()} registrado exitosamente en la Nube!")
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
                precio_dolar = yf.Ticker("MXN=X").fast_info['lastPrice']
                precio_centavos_bushel = yf.Ticker("ZC=F").fast_info['lastPrice']
                
                nuevo_precio_maiz = convertir_precio_chicago(precio_dolar, precio_centavos_bushel)
                
                llave_maiz = "maiz_molido" if "maiz_molido" in base_datos else list(base_datos.keys())[0]
                base_datos[llave_maiz]["costo_kg"] = nuevo_precio_maiz
                
                supabase.table("inventario").update({
                    "stock_kg": float(base_datos[llave_maiz]["stock_kg"]),
                    "costo_kg": float(base_datos[llave_maiz]["costo_kg"])
                }).eq("insumo", llave_maiz).execute()
            
                registrar_bitacora("Radar Chicago", f"Precio del maíz fijado en ${nuevo_precio_maiz} MXN/kg")
                st.success(f"✅ ¡Éxito! Dólar a ${precio_dolar:.2f} MXN. Nuevo precio del Maíz fijado en **${nuevo_precio_maiz} MXN/kg**.")
                time.sleep(3) 
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Los de traje cortaron la conexión: {e}")