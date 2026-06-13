import pandas as pd
import plotly.express as px
import streamlit as st


def render_black_box_page(ctx) -> None:
    supabase = ctx.supabase
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
            
