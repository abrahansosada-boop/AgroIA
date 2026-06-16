import pandas as pd
import streamlit as st


def render_dashboard_page(ctx) -> None:
    db = ctx.db
    st.title("🚜 AgroIA: Centro de Mando")
    st.markdown("Bienvenido al resumen operativo en tiempo real del rancho.")
    
    gasto_real = 0.0
    lotes_reales = 0
    costo_promedio = 0.0
    
    try:

        respuesta_b = db.table("bitacora").select("gasto_total, kilos_procesados").execute()
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
        st.session_state["modulo_actual"] = "Super Laboratorio"

    def saltar_a_inv():
        st.session_state["modulo_actual"] = "Inventario de Insumos"

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        st.info("⚖️ Calcula y optimiza tu revoltura (Manual o IA).")
        st.button(
            "Ir al Súper-Laboratorio",
            width="stretch",
            on_click=saltar_a_lab,
        )

    with col_btn2:
        st.success("📦 Revisa y actualiza tus existencias.")
        st.button(
            "Ir a Inventario de Insumos",
            width="stretch",
            on_click=saltar_a_inv,
        )
