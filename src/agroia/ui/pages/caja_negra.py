import streamlit as st
import pandas as pd
import plotly.express as px
from agroia.repositories.audit import obtener_historial_bitacora
from agroia.domain.finance import calcular_kpis_auditoria, procesar_datos_graficas

def renderizar_caja_negra(supabase):
    st.header("📓 Caja Negra: Historial de Movimientos")
    st.markdown("Auditoría en tiempo real de las operaciones del rancho.")
    
    try:
        with st.spinner("Desencriptando bitácora..."):
            df_bitacora = obtener_historial_bitacora(supabase)
    except Exception as e:
        st.error(f"Error de conexión con la base de datos: {e}")
        return

    st.subheader("📈 Resumen de Operación (Histórico)")
    kpis = calcular_kpis_auditoria(df_bitacora)
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("💰 Gasto Total Auditado", f"${kpis['gasto_total']:,.2f} MXN", "Extraído de DB")
    kpi2.metric("🔄 Movimientos Totales", f"{kpis['total_movimientos']} Registros", "Actividad del rancho")
    kpi3.metric("📉 Auditoría", "Activa", "Sistema Encriptado") 
    
    st.divider()

    if df_bitacora.empty:
        st.info("La bitácora está limpia. Aún no hay movimientos registrados.")
        return

    datos_procesados = procesar_datos_graficas(df_bitacora)
    df_gastos = datos_procesados["df_gastos"]
    df_tiempo = datos_procesados["df_tiempo"]
    df_tabla = datos_procesados["df_tabla"]
    
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
        if not df_tiempo.empty:
            fig_line = px.line(df_tiempo, x='fecha', y='gasto_total', markers=True, title="Gasto Histórico")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Aún no hay tendencia de gastos.")
    
    st.divider()
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        paleta_agro = ['#2ecc71', '#f39c12', '#7f8c8d', '#34495e', '#1abc9c']
        fig_pie = px.pie(df_bitacora, names='accion', title='📊 Distribución de Actividades',
                       hole=0.4, color_discrete_sequence=paleta_agro)
        fig_pie.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_g2:
        st.markdown("### 📥 Exportación Legal")
        st.write("Descarga la matriz de datos para auditorías financieras o fiscales.")
        csv = df_tabla.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Historial a Excel (CSV)",
            data=csv,
            file_name=f'Auditoria_Rancho_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
            use_container_width=True
        )
        
    st.divider()
    st.dataframe(df_tabla, use_container_width=True, hide_index=True)