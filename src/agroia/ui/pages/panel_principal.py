import streamlit as st
from agroia.repositories.audit import obtener_resumen_bitacora
from agroia.domain.finance import calcular_resumen_panel

def renderizar_panel(supabase):
    st.title("🚜 AgroIA: Centro de Mando")
    st.markdown("Bienvenido al resumen operativo en tiempo real del rancho.")
    
    try:
        df_finanzas = obtener_resumen_bitacora(supabase)
        kpis = calcular_resumen_panel(df_finanzas)
    except Exception as e:
        st.error(f"⚠️ Radar financiero desconectado: {e}")
        kpis = {"gasto_real": 0.0, "lotes_reales": 0, "costo_promedio": 0.0}

    st.subheader("📈 Resumen de Operación (Mensual)")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    kpi1.metric(label="💰 Gasto Total Acumulado", value=f"${kpis['gasto_real']:,.2f} MXN")
    kpi2.metric(label="🔄 Lotes / Movimientos", value=f"{kpis['lotes_reales']} Registros")
    kpi3.metric(label="📉 Costo Promedio Histórico", value=f"${kpis['costo_promedio']:,.2f} / Kg")
    
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