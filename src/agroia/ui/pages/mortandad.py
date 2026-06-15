import streamlit as st
from agroia.domain.health import calcular_perdida_mortandad

def renderizar_mortandad(registrar_bitacora):
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
        esta_vacunado = "Sí" in vacunados
        costo_unitario = st.session_state.get('perfil', {}).get('costo_salud', 50.0)
        
        res_mortandad = calcular_perdida_mortandad(bajas, esta_vacunado, costo_unitario)
        
        if not res_mortandad["exito"]:
            st.error(f"⚠️ {res_mortandad['error']}")
        else:
            perdida_medica = res_mortandad["perdida_medica"]
            
            detalle = f"Baja de {bajas} cabezas por {causa}. Fuga de capital médico: ${perdida_medica:.2f}"
            registrar_bitacora("Baja por Mortandad", detalle)
            
            # Actualización del estado global de pérdidas
            st.session_state['fuga_capital'] = st.session_state.get('fuga_capital', 0.0) + perdida_medica

            st.error(f"⚠️ Se dio de baja a {bajas} animal(es). Ya no se contarán para la compra de alimento.")
            
            if perdida_medica > 0:
                st.warning(f"💸 Fuga de capital registrada: Se perdieron **${perdida_medica:.2f} MXN** en medicinas que no se van a recuperar.")
            else:
                st.success("✅ Baja registrada. Afortunadamente no se había invertido dinero médico en estos animales.")