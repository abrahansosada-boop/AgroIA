import streamlit as st

from agroia.data import registrar_bitacora


def render_weight_page(ctx) -> None:
    supabase = ctx.supabase
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
        meta_sugerida = 1.5
        if 'mezcla' in st.session_state:
            meta_sugerida = 0.8 + ((st.session_state['mezcla'].get("proteina", 14.0) - 14.0) * 0.05)

        meta_ia = st.number_input("Meta de ganancia diaria proyectada (kg/día)", value=float(round(meta_sugerida, 2)), step=0.1)

    if st.button("⚖️ Calcular y Registrar Pesada", use_container_width=True):
        if not id_animal:
            st.error("⚠️ Ponle un nombre al Lote o un número al Arete para registrarlo.")
        elif peso_actual <= peso_anterior:
            st.error("⚠️ El peso actual no puede ser menor o igual al anterior. Revisa los datos.")
        else:
            # Calcular GDP (Ganancia Diaria de Peso)
            gdp_real = (peso_actual - peso_anterior) / dias_transcurridos

            st.divider()
            st.subheader("📈 Diagnóstico de Rendimiento")

            c_res1, c_res2, c_res3 = st.columns(3)
            c_res1.metric("Ganancia Total", f"{peso_actual - peso_anterior:.1f} kg")
            c_res2.metric("Ganancia Diaria (Real)", f"{gdp_real:.2f} kg/día", delta=round(gdp_real - meta_ia, 2))
            c_res3.metric("Meta Proyectada", f"{meta_ia:.2f} kg/día")

            if gdp_real >= meta_ia:
                st.success("✅ **EXCELENTE:** El desempeño supera o iguala la proyección de la dieta. ¡Buen trabajo!")
            elif gdp_real >= meta_ia * 0.8:
                st.warning("⚠️ **ALERTA LEVE:** Están ganando peso, pero un poco por debajo de la meta. Revisa el consumo en comederos.")
            else:
                st.error("❌ **PELIGRO:** Los animales están estancados. Revisa sanidad, estrés por clima o corrige la dieta (Módulo 3).")

            detalle = f"Pesada {id_animal}: {peso_actual}kg. GDP: {gdp_real:.2f}kg/día (Meta: {meta_ia})."
            registrar_bitacora(supabase, "Control de Peso", detalle)
            if 'perfil' in st.session_state:
                st.session_state['perfil']['peso'] = peso_actual
                st.success(f"🔄 ¡Sistema Nervioso Activo! El peso base para tus finanzas se actualizó automáticamente a {peso_actual} kg.")
