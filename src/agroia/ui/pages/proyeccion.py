import streamlit as st
from datetime import datetime
from agroia.domain.finance import calcular_proyeccion_financiera

def render_financial_projection_page(ctx) -> None:
    st.header("📈 Centro de Control Financiero")
    
    if 'perfil' not in st.session_state or 'mezcla' not in st.session_state:
        st.error("⚠️ Datos incompletos. Por favor, configure la genética y la dieta de los animales directamente en el **Súper-Laboratorio** para calcular la rentabilidad.")
        return

    perf = st.session_state['perfil']
    mezc = st.session_state['mezcla']
    db = ctx.db
    
    st.subheader("📈 Estrategia de Engorda y Salida")
    tipo_meta = st.radio("¿Cuál es tu objetivo de engorda para este lote?", ["🎯 Meta por Peso (Vender a los X kilos)", "⏳ Meta por Tiempo (Vender a los X meses)"], horizontal=True)
    
    if "Peso" in tipo_meta:
        meta_obj = st.number_input("Peso Objetivo de Venta (kg):", min_value=float(perf["peso"])+10.0, value=300.0, step=10.0)
    else:
        meta_obj = st.number_input("Tiempo máximo en corral (Meses):", min_value=1.0, value=6.0, step=0.5)

    st.divider()
    st.subheader("💰 Inteligencia de Mercado (El Semáforo de Rentabilidad)")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        precio_venta = st.number_input("Precio de Venta en Pie ($/kg):", min_value=10.0, value=85.0, step=1.0)

    # Llamada al dominio puro
    res_finanzas = calcular_proyeccion_financiera(
        peso_actual=perf["peso"], 
        proteina_dieta=mezc["proteina"], 
        costo_dieta_kg=mezc["costo_kg"], 
        precio_venta_kg=precio_venta, 
        tipo_meta=tipo_meta, 
        meta_obj=meta_obj
    )
    
    # Desplegar Info de Días/Meses
    if "Peso" in tipo_meta:
        st.info(f"⏳ A este ritmo de {res_finanzas['ganancia_est']:.2f} kg/día, llegarás a la meta en aprox. **{res_finanzas['dias_faltantes']:.0f} días**.")
    else:
        st.info(f"⚖️ A este ritmo, al cumplir el tiempo, el animal pesará aprox. **{res_finanzas['peso_final_proy']:.1f} kg**.")

    with col_m2:
        st.metric("Costo Producción (por kg)", f"${res_finanzas['costo_kg_carne']:.2f}/kg")

    with col_m3:
        if res_finanzas["estado_fira"] == "APROBADO":
            st.metric("Utilidad Neta Diaria", f"${res_finanzas['ganancia_neta_diaria']:.2f}/día", delta="¡SÚPER RENTABLE!")
            st.success("✅ **APROBADO (Estándar de Alta Eficiencia):** El animal genera $50 o más libres al día. Excelente conversión económica.")
        elif res_finanzas["estado_fira"] == "RIESGO":
            st.metric("Utilidad Neta Diaria", f"${res_finanzas['ganancia_neta_diaria']:.2f}/día", delta="Rentabilidad Baja", delta_color="off")
            st.warning("⚠️ **RIESGO DE RETENCIÓN:** Generas ganancia, pero por debajo de los $50 diarios. Si se alarga la engorda, el costo de mantenimiento te comerá el negocio.")
        else:
            st.metric("Utilidad Neta Diaria", f"${res_finanzas['ganancia_neta_diaria']:.2f}/día", delta="PÉRDIDA", delta_color="inverse")
            st.error("❌ **ALERTA ROJA DE QUIEBRA:** El animal te está costando más de lo que produce. Cambia la mezcla o vende lo más pronto posible.")

    st.divider()
    st.subheader("📄 Ficha Técnica para Inversionistas")
    
    color_borde = "#4CAF50" if res_finanzas['margen_por_kilo'] > 0 else "#F44336"
    estatus = "🟢 NEGOCIO RENTABLE" if res_finanzas['margen_por_kilo'] > 0 else "🔴 ALERTA DE PÉRDIDA"
    
    ficha_html = f"""
    <div style="background-color: #1E1E1E; padding: 25px; border-radius: 15px; border: 2px solid {color_borde}; color: white; font-family: sans-serif;">
        <h2 style="color: {color_borde}; margin-top: 0;">📦 REPORTE DE ENGORDA: {perf['raza'].upper()}</h2>
        <p style="font-size: 14px; color: #AAA; margin-top: -15px;">ESTATUS: {estatus}</p>
        <hr style="border: 0.5px solid #444;">
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td><b>Peso Actual:</b></td><td>{perf['peso']} kg</td></tr>
            <tr><td><b>Proteína Dieta:</b></td><td>{mezc['proteina']:.2f}%</td></tr>
            <tr><td><b>Ganancia Diaria:</b></td><td>{res_finanzas['ganancia_est']:.2f} kg/día</td></tr>
            <tr><td><b>Precio Venta Mercado:</b></td><td>${precio_venta:.2f} MXN/kg</td></tr>
        </table>
        <br>
        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div style="background-color: #2D2D2D; padding: 15px; border-radius: 10px; width: 50%; text-align: center;">
                <span style="font-size: 12px; color: #AAA;">COSTO PRODUCIR 1 KG</span><br>
                <span style="font-size: 24px; font-weight: bold; color: white;">${res_finanzas['costo_kg_carne']:.2f}</span>
            </div>
            <div style="background-color: #2D2D2D; padding: 15px; border-radius: 10px; width: 50%; text-align: center;">
                <span style="font-size: 12px; color: #AAA;">UTILIDAD NETA POR KG</span><br>
                <span style="font-size: 24px; font-weight: bold; color: {color_borde};">${res_finanzas['margen_por_kilo']:.2f}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(ficha_html, unsafe_allow_html=True)
    if res_finanzas['margen_por_kilo'] > 15:
        st.balloons()

    st.divider()
    st.subheader("💾 Respaldar Lote")
    if st.button("Guardar en la Caja Negra"):
        try:
            detalle = f"Proyección {perf['raza'].upper()} | Margen: ${round(res_finanzas['margen_por_kilo'], 2)}/kg | Costo Prod: ${round(res_finanzas['costo_kg_carne'], 2)}/kg"
            
            # Inserción directa a la base de datos usando el contexto (ctx.db)
            db.table("bitacora").insert({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "accion": "Proyección Financiera",
                "detalle": detalle,
                "gasto_total": 0.0
            }).execute()
            
            st.success("✅ ¡Proyección guardada en la Caja Negra de la nube!")
        except Exception as e:
            st.error(f"Error al guardar la proyección: {e}")