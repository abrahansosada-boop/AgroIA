from datetime import datetime

import streamlit as st

from agroia.data import registrar_bitacora


def render_financial_projection_page(ctx) -> None:
    db = ctx.db
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
                
                registrar_bitacora(
                    db,
                    "Proyección Financiera",
                    f"Raza: {perf['raza'].upper()} | "
                    f"Margen: ${round(margen_por_kilo, 2)}/kg | "
                    f"Costo Prod: ${round(costo_kg_carne, 2)}/kg",
                )
                
                st.success("✅ ¡Proyección guardada en la Caja Negra de la nube!")
                
            except Exception as e:
                st.error(f"Error al guardar la proyección: {e}")
    
