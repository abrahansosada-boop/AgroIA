import streamlit as st
from agroia.domain.health import calcular_meta_ganancia, evaluar_rendimiento_pesada

def renderizar_bascula(registrar_bitacora):
    st.header("⚖️ Báscula y Rendimiento")
    st.markdown("Registra el peso real para auditar si la dieta está dando los resultados proyectados.")

    modo_campo = st.toggle("📱 Activar Modo Campo (Pantalla para Celular)")

    es_horizontal = False if modo_campo else True
    tipo_pesaje = st.radio("Método de captura:", ["📊 Promedio por Lote", "🏷️ Individual (Por Arete)"], horizontal=es_horizontal)

    if modo_campo:
        col_b1 = st.container()
        col_b2 = st.container()
        
        st.markdown("<style> div.stButton > button {height: 4.5rem !important; font-size: 22px !important; border: 2px solid #4CAF50;} </style>", unsafe_allow_html=True)
    else:
        col_b1, col_b2 = st.columns(2)

    with col_b1:
        if "Individual" in tipo_pesaje:
            id_animal = st.text_input("ID o Número de Arete", placeholder="Ej. Becerro 405")
        else:
            id_animal = st.text_input("Nombre del Lote", placeholder="Ej. Corral Norte")

        peso_anterior = st.number_input("Peso Anterior (kg)", min_value=1.0, value=180.0, step=10.0)
        peso_actual = st.number_input("Peso Actual (kg)", min_value=1.0, value=200.0, step=10.0)

    with col_b2:
        dias_transcurridos = st.number_input("Días transcurridos entre pesadas", min_value=1, value=15, step=1)
        
        # Extraemos la proteína si existe la dieta en sesión, si no asume 14.0 base
        proteina_actual = st.session_state.get('mezcla', {}).get("proteina", 14.0)
        
        meta_sugerida = calcular_meta_ganancia(proteina_actual)
        meta_ia = st.number_input("Meta de ganancia diaria proyectada (kg/día)", value=meta_sugerida, step=0.1)

    if st.button("⚖️ Calcular y Registrar Pesada", use_container_width=True):
        if not id_animal:
            st.error("⚠️ Ponle un nombre al Lote o un número al Arete para registrarlo.")
            return

        res_pesada = evaluar_rendimiento_pesada(peso_anterior, peso_actual, dias_transcurridos, meta_ia)

        if not res_pesada["exito"]:
            st.error(f"⚠️ {res_pesada['error']}")
        else:
            st.divider()
            st.subheader("📈 Diagnóstico de Rendimiento")

            c_res1, c_res2, c_res3 = st.columns(3)
            c_res1.metric("Ganancia Total", f"{res_pesada['ganancia_total']:.1f} kg")
            c_res2.metric("Ganancia Diaria (Real)", f"{res_pesada['gdp_real']:.2f} kg/día", delta=round(res_pesada['diferencia_meta'], 2))
            c_res3.metric("Meta Proyectada", f"{meta_ia:.2f} kg/día")

            if res_pesada["estado"] == "EXCELENTE":
                st.success(f"✅ **EXCELENTE:** {res_pesada['mensaje']}")
            elif res_pesada["estado"] == "ALERTA":
                st.warning(f"⚠️ **ALERTA LEVE:** {res_pesada['mensaje']}")
            else:
                st.error(f"❌ **PELIGRO:** {res_pesada['mensaje']}")

            detalle = f"Pesada {id_animal}: {peso_actual}kg. GDP: {res_pesada['gdp_real']:.2f}kg/día (Meta: {meta_ia})."
            registrar_bitacora("Control de Peso", detalle)
            
            if 'perfil' in st.session_state:
                st.session_state['perfil']['peso'] = peso_actual
                st.success(f"🔄 ¡Sistema Nervioso Activo! El peso base para tus finanzas se actualizó automáticamente a {peso_actual} kg.")