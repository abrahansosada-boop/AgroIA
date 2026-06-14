import pandas as pd
import pulp
import streamlit as st


def render_laboratory_page(ctx) -> None:
    db = ctx.db
    base_datos = ctx.base_datos
    botiquin = ctx.botiquin
    st.header("🧪 Súper-Laboratorio y Centro de Mando")
    st.markdown("Diseña la genética, audita y optimiza las raciones alimenticias del rancho en una sola pantalla.")
    st.divider()

    # GESTOR DE LOTES INTEGRADO 
    st.subheader("🐄 1. Selección o Creación de Lote")
    
    tab_cargar, tab_crear = st.tabs(["📋 Cargar Lote Activo", "🧬 Crear Nuevo Lote (IA Genética)"])
    
    with tab_cargar:
        col_act, col_ref = st.columns([3, 1])
        
        with col_ref:
            st.button("🔄 Actualizar Lista", width="stretch")

        try:
            respuesta = db.table("perfiles_lotes").select("*").execute()
            
            lotes_guardados = respuesta.data
            
            if lotes_guardados:
                nombres_lotes = [l["nombre_lote"] for l in lotes_guardados]
                
                with col_act:
                    lote_elegido = st.selectbox("Selecciona el lote con el que trabajarás hoy:", nombres_lotes)
                
                if st.button("⚡ Activar Lote para Formulación", width="stretch"):
                    datos_lote = next(item for item in lotes_guardados if item["nombre_lote"] == lote_elegido)
                    
                    st.session_state['perfil'] = {
                        "nombre": datos_lote["nombre_lote"],
                        "raza": datos_lote["raza"],
                        "genero": datos_lote["genero"],
                        "proposito": datos_lote["proposito"],
                        "edad": int(datos_lote["edad"]),
                        "peso": float(datos_lote["peso_promedio"]),
                        "clima": float(datos_lote["clima_local"]),
                        "costo_salud": float(datos_lote["costo_salud"])
                    }
                    
                    st.success(f"✅ ¡Lote **{lote_elegido}** activado! Baja a la sección de dietas.")
            
            else:
                st.info("⚠️ No hay animales en la Nube. Ve a la pestaña 'Crear Nuevo Lote'.")
        
        except Exception as e:
            st.error(f"Error con la bóveda de lotes: {e}")


    with tab_crear:
        st.info("💡 Diseña la genética. Al guardar, quedará blindado en la base de datos.")
        
        nombre_nuevo_lote = st.text_input("Dale un nombre a este grupo:")
        
        # LISTA RAZAS
        razas_disponibles = [
            "brahman", "nelore", "sardo negro", "gyr", "indubrasil", "guzerat",
            "angus", "charolais", "simmental", "hereford", "suizo europeo", "holstein", "limousin", "jersey",
            "brangus (brahman x angus)", "braford (brahman x hereford)", "charbray (brahman x charolais)",
            "simbrah (brahman x simmental)", "simangus (simmental x angus)", "black baldy (angus x hereford)",
            "nelangus (nelore x angus)", "suizo-cebu (suizo x brahman)", "girolando (holstein x gyr)",
            "beefmaster", "brahmousin (brahman x limousin)"
        ]

        with st.form("perfil_animal"):
            col1, col2 = st.columns(2)
            
            with col1:
                raza_sel = st.selectbox("1. Raza:", razas_disponibles)
                genero = st.radio("2. Género:", ["Macho", "Hembra"], horizontal=True)
                proposito = st.selectbox("3. Propósito:", ["Carne", "Leche", "Semental", "Doble Propósito"])
            
            with col2:
                edad = st.number_input("4. Edad (meses):", min_value=1, max_value=200, value=5)
                peso = st.number_input("5. Peso (kg):", min_value=30, max_value=1500, value=180)
                clima = st.slider("6. Clima (°C):", 0, 50, 32)
            
            st.markdown("### 💊 Protocolo Sanitario (Opcional)")
            col_med1, col_med2 = st.columns(2)
            with col_med1:
                nombres_desp = ["❌ Ninguno (No aplicar)"] + [d["nombre"] for d in botiquin["desparasitantes"].values()]
                desp_sel = st.selectbox("Desparasitante", nombres_desp)
            with col_med2:
                nombres_vac = ["❌ Ninguna (No aplicar)"] + [d["nombre"] for d in botiquin["vacunas"].values()]
                vac_sel = st.selectbox("Vacuna Base", nombres_vac)

            enviado = st.form_submit_button("🔥 ANALIZAR Y GUARDAR PERFIL GENÉTICO")
        
        if enviado:
            # LÓGICA DE SALUD OPCIONAL
            if desp_sel == "❌ Ninguno (No aplicar)":
                datos_desp = {"dosis_ml_por_kg": 0, "costo_por_ml": 0, "tiempo_retiro_dias": 0}
            else:
                datos_desp = next(d for d in botiquin["desparasitantes"].values() if d["nombre"] == desp_sel)
                
            if vac_sel == "❌ Ninguna (No aplicar)":
                datos_vac = {"dosis_ml_fija": 0, "costo_por_dosis": 0, "tiempo_retiro_dias": 0}
            else:
                datos_vac = next(d for d in botiquin["vacunas"].values() if d["nombre"] == vac_sel)

            dosis_exacta_ml = peso * datos_desp["dosis_ml_por_kg"]
            costo_desp = dosis_exacta_ml * datos_desp["costo_por_ml"]
            costo_vac = datos_vac["costo_por_dosis"]
            
            costo_salud_total = costo_desp + costo_vac
            retiro_dias = max(datos_desp["tiempo_retiro_dias"], datos_vac["tiempo_retiro_dias"])

            st.divider()
            
            st.subheader("🧬 Dictamen de Inteligencia Genética")
            
            raza = raza_sel.lower()
            
            codex_genetico = {
                # BOS INDICUS (Cebú - Trópico)
                "brahman": {"sangre": "Indicus", "clima": "Trópico/Calor Extremo", "riesgo_termico": "Nulo", "proposito": "Carne"},
                "nelore": {"sangre": "Indicus", "clima": "Trópico/Calor Extremo", "riesgo_termico": "Nulo", "proposito": "Carne"},
                "sardo negro": {"sangre": "Indicus", "clima": "Trópico/Humedad", "riesgo_termico": "Nulo", "proposito": "Doble Propósito"},
                "gyr": {"sangre": "Indicus", "clima": "Trópico/Calor", "riesgo_termico": "Nulo", "proposito": "Leche Tropical"},
                "indubrasil": {"sangre": "Indicus", "clima": "Trópico", "riesgo_termico": "Nulo", "proposito": "Carne"},
                "guzerat": {"sangre": "Indicus", "clima": "Trópico/Árido", "riesgo_termico": "Nulo", "proposito": "Doble Propósito"},
                
                # BOS TAURUS (Europeos - Templado) 
                "angus": {"sangre": "Taurus", "clima": "Templado/Frío", "riesgo_termico": "Crítico (>30°C)", "proposito": "Carne Premium"},
                "charolais": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Alto", "proposito": "Carne (Volumen)"},
                "simmental": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Alto", "proposito": "Doble Propósito"},
                "hereford": {"sangre": "Taurus", "clima": "Templado/Frío", "riesgo_termico": "Crítico (>30°C)", "proposito": "Carne Rústica"},
                "suizo europeo": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Moderado", "proposito": "Doble Propósito"},
                "holstein": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Crítico (>28°C)", "proposito": "Leche Especializada"},
                "limousin": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Alto", "proposito": "Carne (Canal)"},
                "jersey": {"sangre": "Taurus", "clima": "Templado", "riesgo_termico": "Moderado", "proposito": "Leche (Grasa)"},
                
                # CRUZAS Y SINTÉTICAS
                "brangus (brahman x angus)": {"sangre": "Sintética", "clima": "Subtrópico", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "braford (brahman x hereford)": {"sangre": "Sintética", "clima": "Subtrópico", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "charbray (brahman x charolais)": {"sangre": "Sintética", "clima": "Trópico Seco", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "simbrah (brahman x simmental)": {"sangre": "Sintética", "clima": "Subtrópico", "riesgo_termico": "Bajo", "proposito": "Doble Propósito"},
                "simangus (simmental x angus)": {"sangre": "Taurus cruzado", "clima": "Templado", "riesgo_termico": "Moderado", "proposito": "Carne"},
                "black baldy (angus x hereford)": {"sangre": "Taurus cruzado", "clima": "Templado/Frío", "riesgo_termico": "Alto", "proposito": "Carne"},
                "nelangus (nelore x angus)": {"sangre": "Sintética", "clima": "Trópico", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "suizo-cebu (suizo x brahman)": {"sangre": "Sintética", "clima": "Trópico Húmedo", "riesgo_termico": "Bajo", "proposito": "Doble Propósito"},
                "girolando (holstein x gyr)": {"sangre": "Sintética", "clima": "Trópico/Humedad", "riesgo_termico": "Bajo", "proposito": "Leche Tropical"},
                "beefmaster": {"sangre": "Sintética", "clima": "Adaptable", "riesgo_termico": "Bajo", "proposito": "Carne"},
                "brahmousin (brahman x limousin)": {"sangre": "Sintética", "clima": "Subtrópico", "riesgo_termico": "Bajo", "proposito": "Carne"}
            }

            datos_raza = codex_genetico.get(raza_sel.lower(), {"sangre": "Desconocida", "clima": "Variable", "riesgo_termico": "Desconocido", "proposito": "General"})

            st.info(f"🧬 **Perfil Genético:** {datos_raza['sangre']} | 🎯 **Propósito:** {datos_raza['proposito']}")

            if clima >= 35 and datos_raza["riesgo_termico"] in ["Crítico (>30°C)", "Crítico (>28°C)"]:
                st.error(f"❌ **INCOMPATIBILIDAD GRAVE:** Un animal {datos_raza['sangre']} a {clima}°C sufrirá estrés térmico severo y caída de producción ({datos_raza['proposito']}).")
            elif clima >= 30 and datos_raza["riesgo_termico"] == "Alto":
                st.warning(f"⚠️ **RIESGO MODERADO:** La temperatura de {clima}°C está en el límite para esta genética. Vigilar sombra e hidratación.")
            elif datos_raza["riesgo_termico"] == "Nulo":
                st.success(f"✅ **ADAPTABILIDAD PERFECTA:** Genética resistente para {datos_raza['clima']}. Soporta bien los {clima}°C.")
            else:
                st.success(f"⚖️ **CLIMA CONFORTABLE:** Temperatura de {clima}°C dentro del rango de confort para su perfil.")

            try:
                st.divider()
                st.subheader("💊 Receta y Tiempos de Retiro")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Desparasitante", f"{dosis_exacta_ml:.1f} ml", f"${costo_desp:.2f} MXN", delta_color="off")
                col_r2.metric("Vacuna Base", f"{datos_vac['dosis_ml_fija']:.1f} ml", f"${costo_vac:.2f} MXN", delta_color="off")
                col_r3.metric("Inversión Sanitaria", f"${costo_salud_total:.2f} MXN")

                if retiro_dias > 0:
                    st.error(f"🛑 **BLOQUEO COMERCIAL:** Los animales NO pueden ir a rastro en los próximos **{retiro_dias} días** debido a residuos en tejidos.")
                else:
                    st.success("✅ **LIBRE DE RESIDUOS:** Comercialización inmediata autorizada.")
            except NameError:
                st.info("👆 Selecciona los medicamentos arriba y presiona 'Analizar y Guardar' para calcular la receta y los tiempos de retiro.")

            if nombre_nuevo_lote:
                try:
                    db.table("perfiles_lotes").insert({
                        "nombre_lote": nombre_nuevo_lote,
                        "raza": raza_sel,
                        "genero": genero,
                        "proposito": datos_raza["proposito"],
                        "edad": edad,
                        "peso_promedio": peso,
                        "clima_local": clima,
                        "costo_salud": costo_salud_total
                    }).execute()
                    
                    st.success(f"✅ ¡Guardado! Ve a la pestaña 'Cargar Lote' y presiona el botón 'Actualizar Lista'.")
                
                except Exception as e:
                    st.error(f"Error guardando en la Nube: {e}")
            
            else:
                st.error("⚠️ Debes ponerle un nombre al lote arriba para poder guardarlo.")

    # SISTEMA DE FORMULACIÓN
    if st.session_state.get('perfil') is not None:
        perf = st.session_state['perfil']
        peso = float(perf['peso'])
        clima = float(perf['clima'])

        st.divider()
        st.info(f"🟢 **OPERANDO PARA:** Lote '{perf['nombre']}' | Raza: {perf['raza'].upper()} | Peso: {peso} kg | Clima: {clima}°C")

        st.subheader("🧠 Diagnóstico Nutricional Dinámico (IA)")
        consumo_base = peso * 0.03
        prot_meta = 14.0

        if clima >= 35:
            consumo_real = consumo_base * 0.85
            prot_meta = 16.0
            st.error(f"🚨 **ALERTA DE ESTRÉS CALÓRICO ({clima}°C):** El animal está sofocado. Reducirá su consumo a **{consumo_real:.1f} kg/día**. Se exige concentrar la dieta a **{prot_meta}% de Proteína**.")
        elif clima < 20:
            consumo_real = consumo_base * 1.10
            prot_meta = 12.0
            st.info(f"❄️ **ALERTA DE FRÍO ({clima}°C):** El animal comerá más (**{consumo_real:.1f} kg/día**) para calentarse. Sugerimos bajar proteína a **{prot_meta}%** y subir energía.")
        else:
            consumo_real = consumo_base
            st.success(f"✅ **CLIMA CONFORTABLE ({clima}°C):** Consumo normal proyectado de **{consumo_real:.1f} kg/día**. Meta sugerida: **{prot_meta}% de Proteína**.")

        tab_manual, tab_ia = st.tabs(["🛠️ Formulación Manual", "🤖 Piloto Automático (Motor IA)"])

        
        with tab_manual:
            st.markdown("### ⚖️ Auditoría de Mezcla Manual")
            
            filtro = st.radio("Filtrar ingredientes por aporte principal:", ("Todos", "Alta Proteína (>20%)", "Alta Energía (>2.8 Mcal)", "Alta Fibra (>20%)"), horizontal=True)

            lista_filtrada = []
            for insumo, datos in base_datos.items():
                if filtro == "Todos": lista_filtrada.append(insumo)
                elif "Proteína" in filtro and datos.get("proteina_pct", 0) >= 20.0: lista_filtrada.append(insumo)
                elif "Energía" in filtro and datos.get("energia_mcal", 0) >= 2.8: lista_filtrada.append(insumo)
                elif "Fibra" in filtro and datos.get("fibra_pct", 0) >= 20.0: lista_filtrada.append(insumo)

            if not lista_filtrada: st.warning("No hay insumos en tu bodega que cumplan este filtro.")

            if "receta_guardada_ia" in st.session_state:
                st.success("🤖 Receta de la IA detectada en la memoria.")
                if st.button("📥 Importar Receta a la Mesa de Trabajo", key="btn_importar_unica"):
                    st.session_state["memoria_selector"] = st.session_state["receta_guardada_ia"]["ingredientes"]
                    for ins, kg in st.session_state["receta_guardada_ia"]["kilos"].items():
                        st.session_state[f"kg_{ins}"] = kg

            seleccionados = st.multiselect("Seleccione los ingredientes a utilizar:", lista_filtrada, key="memoria_selector")

            mezcla_final = []
            total_kilos_mezcla = 0

            if seleccionados:
                cols = st.columns(len(seleccionados))
                for i, insumo in enumerate(seleccionados):
                    with cols[i]:
                        kilos = st.number_input(f"Kg de {insumo}", min_value=0.0, step=1.0, key=f"kg_{insumo}")
                        mezcla_final.append({"nombre": insumo, "kilos": kilos, "datos": base_datos[insumo]})
                        total_kilos_mezcla += kilos

            if st.button("⚖️ AUDITAR MEZCLA MANUAL"):
                if total_kilos_mezcla > 0:
                    prot_acum = sum((item["kilos"] * item["datos"]["proteina_pct"]) for item in mezcla_final) / total_kilos_mezcla
                    ener_acum = sum((item["kilos"] * item["datos"]["energia_mcal"]) for item in mezcla_final) / total_kilos_mezcla
                    fibr_acum = sum((item["kilos"] * item["datos"]["fibra_pct"]) for item in mezcla_final) / total_kilos_mezcla
                    costo_tot = sum((item["kilos"] * item["datos"]["costo_kg"]) for item in mezcla_final)

                    st.session_state['mezcla'] = {
                        "proteina": prot_acum, "energia": ener_acum, "fibra": fibr_acum,
                        "costo_total": costo_tot, "total_kilos": total_kilos_mezcla,
                        "costo_kg": costo_tot / total_kilos_mezcla, "detalle": mezcla_final
                    }
                    st.success("✅ Auditoría completada")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Proteína Cruda", f"{prot_acum:.2f}%")
                    c2.metric("Energía Metab.", f"{ener_acum:.2f} Mcal")
                    c3.metric("Fibra (FDN)", f"{fibr_acum:.2f}%")

                    st.divider()
                    st.subheader("📊 Radiografía Detallada por Insumo")
                    datos_desglose = []
                    for item in mezcla_final:
                        kg_ingrediente = item["kilos"]
                        pct_mezcla = (kg_ingrediente / total_kilos_mezcla) * 100
                        kg_proteina = kg_ingrediente * (item["datos"]["proteina_pct"] / 100)
                        datos_desglose.append({
                            "Insumo": item["nombre"].upper(), "Participación (%)": round(pct_mezcla, 2),
                            "Aporte Proteína (kg)": round(kg_proteina, 2), "Costo en Mezcla ($)": round(kg_ingrediente * item["datos"]["costo_kg"], 2)
                        })

                    df_desglose = pd.DataFrame(datos_desglose)
                    st.dataframe(df_desglose, width="stretch")
                    
                    if prot_acum > 18.0: st.warning("⚠️ RIESGO: Nivel de proteína muy alto. Podría causar estrés renal.")
                    elif fibr_acum < 10.0: st.warning("⚠️ RIESGO: Fibra muy baja. Peligro inminente de acidosis ruminal.")

                    st.session_state['mezcla_lista'] = {
                        "total_kilos": float(total_kilos_mezcla), "costo_total": float(costo_tot), "proteina": float(prot_acum)
                    }
                else:
                    st.error("Agregue kilos a los ingredientes.")

            if 'mezcla_lista' in st.session_state:
                st.divider()
                if st.button(
                    "💾 Procesar Lote Manual y Registrar Gasto",
                    width="stretch",
                ):
                    m = st.session_state['mezcla_lista']
                    detalle_txt = f"Lote MANUAL de {m['total_kilos']}kg al {m['proteina']:.1f}% de proteína."
                    try:
                        db.table("bitacora").insert({"accion": "Preparación Manual", "detalle": detalle_txt, "gasto_total": m['costo_total'], "kilos_procesados": m['total_kilos']}).execute()
                        st.success(f"✅ ¡Dinero auditado! Se registraron ${m['costo_total']:,.2f} MXN en la Nube.")
                        del st.session_state['mezcla_lista']
                    except Exception as e:
                        st.error(f"⚠️ Error al conectar con la bóveda: {e}")

            st.divider()
            st.subheader("⚖️ Corrector de Mezcla (Cuadrado de Pearson)")
            
            opciones_ingredientes = list(base_datos.keys())
            
            if not opciones_ingredientes:
                st.warning("⚠️ Bodega vacía. Agrega insumos para usar el corrector.")
            else:
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    prot_actual = st.number_input("Proteína actual de la mezcla (%)", value=11.0, step=0.5)
                    kilos_en_tolva = st.number_input("Kilos actuales en la revolvedora", value=1000, step=100)
                with col_p2:
                    prot_objetivo = st.number_input("Proteína objetivo (%)", value=14.0, step=0.5)
                    ing_refuerzo = st.selectbox("Selecciona ingrediente de refuerzo:", opciones_ingredientes)
                
                if ing_refuerzo:
                    prot_refuerzo = base_datos[ing_refuerzo].get("proteina_pct", 0)

                    if st.button("🧮 Calcular Corrección"):
                        if prot_objetivo <= prot_actual or prot_objetivo >= prot_refuerzo:
                            st.error("❌ Misión Imposible: La proteína objetivo debe estar ENTRE la actual y la del refuerzo.")
                        else:
                            partes_refuerzo = abs(prot_objetivo - prot_actual)
                            partes_mezcla = abs(prot_refuerzo - prot_objetivo)
                            kilos_a_añadir = (kilos_en_tolva / partes_mezcla) * partes_refuerzo
                            st.success(f"**Resultado:** Añade **{kilos_a_añadir:.2f} kg** de **{ing_refuerzo.upper()}** para lograr el {prot_objetivo}%.")

        # PESTAÑA: MOTOR IA
        with tab_ia:
            st.subheader("📊 Radar de Costo-Beneficio (Proteína Barata)")
            analisis_prot = []
            for ins, datos in base_datos.items():
                if datos.get("proteina_pct", 0) > 2.0:
                    costo_por_punto = datos["costo_kg"] / datos["proteina_pct"]
                    analisis_prot.append({
                        "Insumo": ins.title().replace("_", " "), "Costo por Punto": f"${costo_por_punto:.2f}",
                        "Proteína Total": f"{datos['proteina_pct']}%", "Costo x Kg": f"${datos['costo_kg']:.2f}"
                    })
            st.dataframe(
                sorted(
                    analisis_prot,
                    key=lambda x: float(
                        x["Costo por Punto"].replace("$", "")
                    ),
                ),
                width="stretch",
            )
            st.divider()

            st.markdown("### 🎛️ Motor de Optimización Lineal")
            col_sis, col_etapa = st.columns(2)
            with col_sis: sistema = st.radio("1. Sistema de Producción:", ["🏡 Estabulado (Corral)", "🌿 Pastoreo (Suplemento)"])
            with col_etapa: etapa = st.selectbox("2. Etapa de Vida:", ["🍼 Inicio (Desarrollo de Rumen)", "📈 Desarrollo (Crecimiento)", "🥩 Finalización"])

            usar_promotores = st.toggle("💊 Incluir Promotores / Ionóforos (Ej. Monensina)")
            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                req_proteina = st.number_input("🎯 Objetivo de Proteína (%)", min_value=5.0, max_value=30.0, value=float(prot_meta), step=0.5)
            with col2:
                req_energia = st.number_input("⚡ Objetivo de Energía (Mcal)", min_value=1.0, max_value=4.0, value=2.5, step=0.1)


            if st.button("🧠 GENERAR FÓRMULA ÓPTIMA"):
                prob = pulp.LpProblem("Dieta_Barata", pulp.LpMinimize)
                insumos = list(base_datos.keys())
                # TODO: Migrate PuLP variable creation / CBC solver setup before upgrading to PuLP 4.
                x = pulp.LpVariable.dicts("Ingrediente", insumos, lowBound=0)

                prob += pulp.lpSum([x[i] * base_datos[i]["costo_kg"] for i in insumos]), "Costo"
                prob += pulp.lpSum([x[i] for i in insumos]) == 100, "Peso_100"
                prob += pulp.lpSum([x[i] * base_datos[i]["proteina_pct"] for i in insumos]) >= req_proteina * 100, "Req_Prot"
                prob += pulp.lpSum([x[i] * base_datos[i]["energia_mcal"] for i in insumos]) >= req_energia * 100, "Req_Ener"

                for i in insumos:
                    if "max_pct" in base_datos[i]:
                        prob += x[i] <= base_datos[i]["max_pct"], f"Max_{i}"

                toxicos = [i for i in ["urea_agricola", "pollinaza", "harina_pescado"] if i in insumos]
                if "urea_agricola" in toxicos: prob += x["urea_agricola"] <= 0.5, "Tope_Urea"
                if "pollinaza" in toxicos: prob += x["pollinaza"] <= 12.0, "Tope_Pollinaza"
                if "harina_pescado" in toxicos: prob += x["harina_pescado"] <= 4.0, "Tope_Pescado"
                if len(toxicos) >= 2: prob += pulp.lpSum([x[i] for i in toxicos]) <= 11.0, "Colchon_Paranoia_Palatabilidad"

                prob.solve()

                if pulp.LpStatus[prob.status] == "Optimal":
                    resultados = []
                    costo_cien_kg = 0
                    for i in insumos:
                        if x[i].varValue > 0.01:
                            costo_ing = x[i].varValue * base_datos[i]["costo_kg"]
                            costo_cien_kg += costo_ing
                            resultados.append({
                                "Insumo": i.upper(), "Kilos por 100kg": round(x[i].varValue, 2),
                                "Costo ($)": round(costo_ing, 2)
                            })

                    st.session_state['solucion_ia'] = {
                        "df": pd.DataFrame(resultados), "costo_kg": costo_cien_kg / 100,
                        "detalles_ia": { "ingredientes": [i for i in insumos if x[i].varValue > 0.01], "kilos": {i: float(x[i].varValue) for i in insumos if x[i].varValue > 0.01} },
                        "proteina_log": req_proteina, "energia_log": req_energia
                    }
                    st.balloons()
                else:
                    st.session_state['solucion_ia'] = None
                    st.error("❌ Misión Imposible. Faltan ingredientes para esta meta.")

            if 'solucion_ia' in st.session_state and st.session_state['solucion_ia'] is not None:
                sol = st.session_state['solucion_ia']

                st.success("✅ ¡Fórmula óptima encontrada!")
                st.title(f"💰 Costo final proyectado: ${sol['costo_kg']:.2f} MXN / kg")
                st.dataframe(sol['df'], width="stretch", hide_index=True)

                st.divider()
                st.markdown("### 🚜 Auto-Formulador de Lote (Revolvedora IA)")
                st.info(f"Usando el consumo biológico calculado: **{consumo_real:.1f} kg/día** por animal.")

                with st.form("form_tolva_ia"):
                    c_lote1, c_lote2 = st.columns(2)
                    with c_lote1: num_cabezas = st.number_input("Número de Animales a alimentar:", min_value=1, value=50, step=5)
                    with c_lote2: dias_dieta = st.number_input("¿Para cuántos días vas a preparar?", min_value=1, value=3, step=1)
                    
                    btn_tolva = st.form_submit_button(
                        "🤖 Generar Receta de Tolva y Pagar Lote",
                        width="stretch",
                    )

                if btn_tolva:
                    kilos_totales_ia = num_cabezas * consumo_real * dias_dieta
                    costo_lote_ia = kilos_totales_ia * sol['costo_kg']

                    st.success(f"✅ **¡Tolva Calculada!** Mezcla exactamente esto en tu revolvedora para **{kilos_totales_ia:,.0f} kg** totales:")

                    receta_tolva = []
                    for index, row in sol['df'].iterrows():
                        kg_insumo_tolva = (row["Kilos por 100kg"] / 100) * kilos_totales_ia
                        receta_tolva.append({"Insumo": row["Insumo"], "Kilos a echar a la Tolva": round(kg_insumo_tolva, 1)})

                    st.dataframe(
                        pd.DataFrame(receta_tolva),
                        width="stretch",
                        hide_index=True,
                    )
                    st.metric("💰 Costo Total del Lote", f"${costo_lote_ia:,.2f} MXN")

                    try:
                        detalle = f"Lote IA Tolva: {kilos_totales_ia:,.0f}kg al {sol['proteina_log']}% de prot."
                        db.table("bitacora").insert({"accion": "Preparación IA", "detalle": detalle, "gasto_total": costo_lote_ia, "kilos_procesados": kilos_totales_ia}).execute()

                        st.session_state['mezcla'] = {
                            "proteina": sol['proteina_log'], "energia": sol['energia_log'], "fibra": 10.0,
                            "costo_total": costo_lote_ia, "total_kilos": kilos_totales_ia,
                            "costo_kg": sol['costo_kg'], "detalle": "Fórmula IA Optimizada"
                        }
                        st.success(f"✅ ¡Gastos Registrados! Ya puedes ir al Módulo 4: Proyecciones Financieras.")
                    except Exception as e:
                        st.error(f"⚠️ Error al registrar en la bóveda: {e}")
