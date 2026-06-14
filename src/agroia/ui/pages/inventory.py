import pandas as pd
import streamlit as st
import yfinance as yf

from agroia.data import registrar_bitacora


def render_inventory_page(ctx) -> None:
    db = ctx.db
    base_datos = ctx.base_datos
    es_administrador = ctx.es_administrador
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
    st.dataframe(df_inventario, width="stretch", hide_index=True)
    
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

    if st.button("💾 Registrar Movimiento en Bóveda", width="stretch"):
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

                respuesta = db.table("inventario").update({
                    "stock_kg": float(nuevo_stock),
                    "costo_kg": float(precio_final)
                }).eq("insumo", insumo_edit).execute()

                base_datos[insumo_edit]["stock_kg"] = float(nuevo_stock)
                base_datos[insumo_edit]["costo_kg"] = float(precio_final)
                
                registrar_bitacora(db, tipo_accion, detalle)
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
                
                db.table("inventario").update({
                "stock_kg": float(base_datos[llave_maiz]["stock_kg"]),
                "costo_kg": float(base_datos[llave_maiz]["costo_kg"])
            }).eq("insumo", llave_maiz).execute()
            
            
                registrar_bitacora(
                    db,
                    "Radar Chicago",
                    f"Precio del maíz fijado en ${nuevo_precio_maiz} MXN/kg",
                )
                    
                st.success(f"✅ ¡Éxito! Dólar a ${precio_dolar:.2f} MXN. Nuevo precio del Maíz fijado en **${nuevo_precio_maiz} MXN/kg**.")
                import time
                time.sleep(3) 
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Los de traje cortaron la conexión: {e}")
