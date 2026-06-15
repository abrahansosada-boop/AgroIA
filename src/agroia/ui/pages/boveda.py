import streamlit as st
from agroia.domain.nutrition import (calcular_rendimiento_nopal, 
    calcular_rotacion_prv, 
    calcular_biomasa_azolla, 
    calcular_enriquecimiento_esquilmos, 
    calcular_silo_tamo, 
    calcular_proyeccion_sspi, 
    calcular_efecto_boma, 
    calcular_roi_cercos_virtuales
)
# 👑 MÓDULO: BÓVEDA PREMIUM DE GANADERÍA REGENERATIVA & RESILIENCIA GLOBAL
def renderizar_boveda(base_datos):
    st.title("👑 Bóveda Premium: Hub Global de Tecnologías Resilientes")
    st.markdown("""
        Este módulo recopila sistemas de manejo y optimización de recursos forrajeros validados en ecosistemas de alta adversidad climatológica. Diseñado para reducir la dependencia de insumos externos y mitigar los efectos de sequías prolongadas mediante protocolos operativos estandarizados.
    """)

    # Selector de los 3 Pilares de Impacto Global
    pilar_seleccionado = st.selectbox(
        "🌍 Seleccione un Pilar de Resiliencia:",
        [
            "🌵 Pilar 1: Resiliencia Extrema y Escasez (Supervivencia Hídrica y Alimentaria)",
            "🦠 Pilar 2: Suelo, Microbiología y Reducción de Insumos (Regeneración)",
            "📡 Pilar 3: Escalabilidad y Manejo Dinámico (Procesos y Tecnología)"
        ]
    )

    st.divider()

    # 🌵 PILAR 1: RESILIENCIA EXTREMA Y ESCASEZ
    if "Pilar 1" in pilar_seleccionado:
        st.subheader("🛡️ Tácticas de Supervivencia ante Sequías e Inflación de Insumos")
        
        tech_p1 = st.radio(
            "Seleccione la Tecnología a Desplegar:",
            ["🌵 Bio-Fábrica de Nopal Forrajero", "🌱 Cultivo Rústico de Azolla", "🌾 Enriquecimiento de Esquilmos"]
        )
        
        # NOPAL
        if "Nopal" in tech_p1:
            st.markdown("### 📊 Calculadora de Biomasa (Nopal)")
            c1, c2, c3 = st.columns(3)
            with c1: 
                densidad = st.number_input("Plantas por Hectárea:", value=10000, step=1000)
            with c2: 
                peso_penca = st.number_input("Peso prom. por penca (kg):", value=1.2, step=0.1)
            with c3: 
                pencas_planta = st.number_input("Pencas a cosechar por planta:", value=4, step=1)
            
            ton_ha = calcular_rendimiento_nopal(densidad, peso_penca, pencas_planta)
            st.info(f"**Rendimiento Proyectado:** {ton_ha:,.1f} Toneladas por Hectárea")

        # AZOLLA 
        elif "Azolla" in tech_p1:
            st.markdown("### 🌱 Calculadora de Biomasa (Azolla)")
            c1, c2 = st.columns(2)
            with c1:
                espejos = st.number_input("Cantidad de espejos de agua:", min_value=1, value=2, step=1)
                m2_espejo = st.number_input("Metros cuadrados por espejo:", min_value=1.0, value=10.0, step=1.0)
            with c2:
                cosecha_m2 = st.number_input("Cosecha estimada (kg/m2):", min_value=0.1, value=1.5, step=0.1)
                dias_cosecha = st.number_input("Días por ciclo de cosecha:", min_value=1, value=15, step=1)

            resultados_azolla = calcular_biomasa_azolla(espejos, m2_espejo, cosecha_m2, dias_cosecha)

            st.divider()
            st.subheader("📊 Veredicto de Producción")
            r1, r2 = st.columns(2)
            r1.metric("Producción por Ciclo", f"{resultados_azolla['ciclo_kg']:,.1f} kg", f"Cada {dias_cosecha} días")
            r2.metric("Proyección Anual", f"{resultados_azolla['anual_ton']:,.2f} Toneladas", "Biomasa rica en proteína")

        # ESQUILMOS
        elif "Esquilmos" in tech_p1:
            st.markdown("### 🌾 Tratamiento y Enriquecimiento de Esquilmos")
            c1, c2 = st.columns(2)
            with c1:
                toneladas = st.number_input("Toneladas de esquilmo seco (paja/rastrojo):", min_value=1.0, value=10.0, step=1.0)
                precio_ton = st.number_input("Precio de compra ($/Ton):", min_value=0.0, value=1000.0, step=100.0)
            with c2:
                tratamiento = st.selectbox(
                    "Tipo de Tratamiento Básico:", 
                    ["Urea y Melaza", "Amonificación", "Inoculación de Hongos (Pleurotus)"]
                )
            
            resultados_esquilmos = calcular_enriquecimiento_esquilmos(toneladas, precio_ton, tratamiento)

            st.divider()
            st.subheader("📊 Veredicto de Enriquecimiento")
            r1, r2, r3 = st.columns(3)
            r1.metric("Costo Final (Ton)", f"${resultados_esquilmos['costo_final_ton']:,.2f} MXN", "Ya con tratamiento")
            r2.metric("Incremento de Proteína", f"+{resultados_esquilmos['incremento_pc']}% PC", "Valor nutricional añadido")
            r3.metric("Costo Total del Lote", f"${resultados_esquilmos['costo_total']:,.2f} MXN", f"Por {toneladas} Ton")

        # SILO DE TAMO
        elif "Silo" in tech_p1:
            st.markdown("### 🛢️ Calculadora de Silo de Tamo (Fermentación Sólida)")
            
            insumos_bodega = getattr(base_datos, "insumos_disponibles", {})
            precio_real_melaza = insumos_bodega.get("melaza", {}).get("costo_kg", 0.0)
            
            if precio_real_melaza == 0.0:
                st.warning("⚠️ No se detectó el precio de la 'melaza' en el inventario de la bodega. Se calculará con costo $0.0 de forma temporal.")

            c1, c2 = st.columns(2)
            with c1:
                toneladas = st.number_input("Toneladas de Tamo Seco:", min_value=1.0, value=5.0, step=1.0)
                precio_tamo = st.number_input("Precio del Tamo ($/Ton):", min_value=0.0, value=800.0, step=100.0)
            with c2:
                agua_ton = st.number_input("Agua para 60% humedad (Lts/Ton):", min_value=500.0, value=1250.0, step=50.0)
                melaza = st.number_input("Melaza (Lts por Ton):", min_value=0.0, value=20.0, step=5.0)
            
            res_silo = calcular_silo_tamo(toneladas, precio_tamo, melaza, precio_real_melaza, agua_ton)
            
            st.divider()
            st.subheader("📊 Formulación de Ensilaje")
            r1, r2, r3 = st.columns(3)
            r1.metric("Agua a Inyectar", f"{res_silo['agua_requerida_lts']:,.0f} Lts")
            r2.metric("Biomasa Final (Húmeda)", f"{res_silo['peso_final_ton']:,.1f} Ton")
            r3.metric("Costo por Ton Ensilada", f"${res_silo['costo_ton_ensilada']:,.2f} MXN", f"Gasto total calculado con precio de inventario (${precio_real_melaza}/unit): ${res_silo['costo_total']:,.2f}")


    # 🦠 PILAR 2: SUELO Y MICROBIOLOGÍA
    elif "Pilar 2" in pilar_seleccionado:
        st.subheader("🦠 Regeneración Biológica del Suelo y Control Sanitario Natural")
        tech_p2 = st.radio("Seleccione la Tecnología Operativa:", ["🌳 Sistemas Silvopastoriles Intensivos (SSPi)", "🐄 Efecto Boma (Corrales Móviles)"], horizontal=True)
        st.divider()

        # MODULO SSPI
        if "Silvopastoriles" in tech_p2:
            st.markdown("### 🌳 Sistemas Silvopastoriles Intensivos (SSPi)")
            st.caption("📍 Origen de validación: Modelos tropicales y subtropicales de alta densidad")

            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "ALTO", "Inversión inicial en siembra", delta_color="inverse")
            col_v2.metric("🇲🇽 Acceso en México", "ALTO", "Semillas endémicas locales", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "MEDIA", "Requiere descansos estrictos", delta_color="off")

            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Proyección de Carga Animal"])

            with tab_info:
                st.markdown("#### 📖 Concepto Técnico")
                st.write("Integración de arbustos forrajeros en hileras dentro de los potreros. Triplica la biomasa comestible por metro cuadrado (crecimiento vertical) y provee sombra para confort animal.")
                
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Incremento de carga animal por hectárea sin uso de fertilizantes químicos.
                        * Mitigación de estrés calórico en el ganado.
                        * Fijación biológica de nitrógeno en suelos degradados.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * **TIEMPO DE ESTABLECIMIENTO:** No introducir ganado hasta que los arbustos alcancen 1.5 metros de altura (aprox. 6 a 8 meses).
                        * **TOXICIDAD:** Especies como Leucaena requieren un periodo de adaptación paulatina para la flora ruminal.
                    """)

                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Preparación de suelo:** Subsoleo y trazo de surcos siguiendo curvas de nivel.
                    2. **Siembra:** Hileras de arbustos separadas a 1.5 - 2.0 metros, intercaladas con pasto.
                    3. **Establecimiento:** Exclusión total de animales por 6-8 meses.
                    4. **Pastoreo:** Ramoneo intensivo por periodos cortos (12-24 horas) y descansos largos (40-60 días).
                """)

            with tab_receta:
                st.markdown("#### 🧮 Calculadora de Expansión del Rancho")
                st.write("Proyecte el incremento de capacidad instalada sin adquirir nuevas tierras:")

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    hectareas = st.number_input("Hectáreas del potrero a sembrar:", min_value=1.0, value=10.0, step=1.0)
                    carga = st.number_input("Carga animal actual (Vacas/Hectárea):", min_value=0.1, value=1.0, step=0.1)
                with col_c2:
                    multiplicador = st.slider("Multiplicador de biomasa esperado:", min_value=1.5, max_value=5.0, value=3.0, step=0.5)
                    valor_vaca = st.number_input("Valor comercial promedio por vaca ($):", min_value=5000, value=25000, step=1000)

                res_sspi = calcular_proyeccion_sspi(hectareas, carga, multiplicador, valor_vaca)

                st.subheader("📊 Nuevo Límite Biológico del Rancho")
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Carga Actual (Total)", f"{res_sspi['vacas_actuales_totales']:.0f} Cabezas")
                col_r2.metric("Nueva Carga SSPi", f"{res_sspi['vacas_nuevas_totales']:.0f} Cabezas", f"+{res_sspi['incremento_vacas']:.0f} espacios nuevos")
                col_r3.metric("Densidad Operativa", f"{res_sspi['carga_proyectada']:.1f} Vacas/Ha")

                st.divider()
                st.markdown("##### 💵 Valorización de Activos Biológicos")
                st.metric("Incremento de Capital Soportado", f"${res_sspi['valor_capital_adicional']:,.2f} MXN", "Capacidad extra del rancho valorizada en ganado")

        # MODULO EFECTO BOMA
        elif "Boma" in tech_p2:
            st.markdown("### 🐄 Efecto Boma (Corrales Móviles Nocturnos)")
            st.caption("📍 Origen de validación: Sabanas africanas (Manejo Holístico) y tierras áridas")

            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "MUY BAJO", "Costo de hilo eléctrico móvil", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "INMEDIATO", "Cero insumos externos", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "ALTA", "Exige movimiento diario", delta_color="inverse")

            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Ingeniería de Corral y Fertilizante"])

            with tab_info:
                st.markdown("#### 📖 Concepto Operativo")
                st.write("Confinamiento nocturno de alta densidad utilizando cercos móviles sobre áreas de suelo degradado. El impacto físico de las pezuñas rompe la costra del suelo, mientras que la concentración de excretas inyecta fertilidad biológica masiva.")
                
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Rehabilitación de zonas severamente degradadas o desnudas.
                        * Incorporación masiva de materia orgánica a costo cero.
                        * Protección contra depredadores nocturnos.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * **ZONAS INUNDABLES:** Evitar en temporada de lluvias intensas. El lodo profundo causa afecciones podales graves.
                        * **ESTANCIA PROLONGADA:** Prohibido dejar a los animales más de 12 horas en el mismo polígono.
                    """)

                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Selección del sitio:** Identificar el parche de tierra más estéril del potrero.
                    2. **Instalación:** Armar corral perimetral calculando 3 m² por Unidad Animal.
                    3. **Encierro:** Introducir al hato al caer la tarde.
                    4. **Rotación:** Al amanecer, abrir el corral, sacar al ganado a pastorear y mover la estructura.
                """)

            with tab_receta:
                st.markdown("#### 🧮 Dimensionamiento Físico y Químico")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    num_vacas = st.number_input("Número de cabezas a confinar:", min_value=10, value=100, step=10)
                with col_c2:
                    peso_promedio = st.number_input("Peso promedio por animal (kg):", min_value=100, value=400, step=10)

                # Mantenemos la regla estricta: jalamos el costo real de la base de datos
                costo_urea_bd = float(base_datos.get("urea_agricola", {}).get("costo_kg", 15.0))
                
                # Llamada al dominio puro
                res_boma = calcular_efecto_boma(num_vacas, peso_promedio, costo_urea_bd)

                st.subheader("📐 Especificaciones Estructurales")
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("Área Requerida", f"{res_boma['area_m2']:.1f} m²", "Confinamiento de alta densidad")
                col_r2.metric("Perímetro de Cerco", f"{res_boma['perimetro_metros']:.1f} metros lineales", "Diseño cuadrangular")

                st.divider()

                st.markdown("##### 💵 Ahorro Equivalente en Agroquímicos")
                
                costo_urea_usuario = st.number_input("Precio de la Urea Química ($/kg):", min_value=1.0, value=costo_urea_bd, step=1.0, key="costo_urea_boma")
                
                if costo_urea_usuario != costo_urea_bd:
                    res_boma = calcular_efecto_boma(num_vacas, peso_promedio, costo_urea_usuario)

                col_f1, col_f2 = st.columns(2)
                col_f1.metric("Estiércol y Orina", f"{res_boma['excretas_noche_kg']:,.1f} kg / noche")
                col_f2.metric("Ahorro Operativo", f"${res_boma['ahorro_diario']:,.2f} / noche", f"Equivalente a {res_boma['urea_equivalente_kg']:.1f} kg de Urea")

    # 📡 PILAR 3: ESCALABILIDAD Y PROCESOS
    elif "Pilar 3" in pilar_seleccionado:
        st.subheader("📡 Escalabilidad y Manejo Dinámico (Procesos y Tecnología)")
        tech_p3 = st.radio("Seleccione la Tecnología Operativa:", ["🛰️ Cercos Virtuales (Collares GPS)", "📊 Pastoreo Holístico (Aforo Diario)"], horizontal=True)
        st.divider()

        # MODULO CERCOS VIRTUALES
        if "Cercos" in tech_p3:
            st.markdown("### 🛰️ Cercos Virtuales (Collares GPS y Telemetría)")
            st.caption("📍 Origen de validación: Estaciones experimentales y ganadería de precisión")

            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "ALTO", "Adquisición de Hardware", delta_color="inverse")
            col_v2.metric("🇲🇽 Acceso en México", "MEDIO", "Importación tecnológica", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "ALTA", "Uso de software georreferenciado", delta_color="inverse")

            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Análisis de Capitalización (ROI)"])

            with tab_info:
                st.markdown("#### 📖 Concepto Operativo")
                st.write("Sustitución de barreras físicas por dispositivos de control individual (collares). Emiten estímulos auditivos y sensoriales para confinar al ganado dentro de polígonos virtuales trazados en plataformas digitales.")
                
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Implementación de rotación ultra-intensiva sin inversión en alambres.
                        * Exclusión estricta de zonas ecológicas (cuerpos de agua, reforestaciones).
                        * Mitigación de costos de nómina por patrullaje y reparación de cercos.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * **TOPOGRAFÍA:** Inoperable en zonas con nula cobertura de red celular o señal satelital deficiente.
                        * **PERÍMETROS EXTERNOS:** El sistema NO exime la necesidad de un cerco físico exterior robusto para prevenir robos o invasión a carreteras.
                    """)

                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Equipamiento:** Colocación del hardware en el 100% del hato a controlar.
                    2. **Calibración:** Periodo de entrenamiento (3-5 días) en potrero físico cerrado para asociación neurológica del estímulo.
                    3. **Programación:** Trazo diario de polígonos de pastoreo mediante aplicación móvil o web.
                    4. **Telemetría:** Monitoreo remoto de mapas de calor, niveles de batería y alertas de fuga.
                """)

            with tab_receta:
                st.markdown("#### 💵 Impacto Financiero: Tecnología vs Infraestructura Tradicional")
                st.write("Proyección comparativa del costo de hardware versus el levantamiento de cercos físicos divisores.")

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    km_cerco_evitados = st.number_input("Kilómetros de cerco físico a sustituir:", min_value=1.0, value=10.0, step=1.0)
                    costo_km_cerco = st.number_input("Costo promedio de 1 km de cerco ($):", min_value=10000.0, value=35000.0, step=5000.0)
                with col_c2:
                    cabezas_a_equipar = st.number_input("Número de cabezas (collares requeridos):", min_value=1, value=50, step=5)
                    costo_collar_unitario = st.number_input("Costo unitario por collar GPS ($):", min_value=1000.0, value=3000.0, step=500.0)

                res_cercos = calcular_roi_cercos_virtuales(km_cerco_evitados, costo_km_cerco, cabezas_a_equipar, costo_collar_unitario)
                
                st.subheader("📊 Diagnóstico de Retorno de Inversión")
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Gasto en Cerco Físico", f"${res_cercos['inversion_cerco_fisico']:,.2f}", delta_color="inverse")
                col_r2.metric("Inversión en Collares", f"${res_cercos['inversion_collares']:,.2f}", delta_color="off")
                
                if res_cercos['ahorro_infraestructura'] > 0:
                    col_r3.metric("Capital a Favor", f"${res_cercos['ahorro_infraestructura']:,.2f}", "Punto de equilibrio superado")
                else:
                    col_r3.metric("Déficit de Inversión", f"${res_cercos['ahorro_infraestructura']:,.2f}", "Costo de hardware excede infraestructura", delta_color="inverse")

        # MODULO PASTOREO HOLISTICO
        elif "Pastoreo" in tech_p3:
            st.markdown("### 📊 Pastoreo Holístico (Gestión de Aforos)")
            st.info("**¿Qué es?** En lugar de dejar a las vacas sueltas en un potrero gigante por un mes, divides el potrero en secciones pequeñas. Las vacas entran, comen todo parejo por 1 o 2 días, y las mueves a la siguiente sección. **Resultado:** El pasto recibe descansos largos para crecer más fuerte y evitas que el rancho se llene de maleza.")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "BAJO", "Uso de recursos existentes", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "INMEDIATO", "Metodología de rotación", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "ALTA", "Exige medir pasto y mover ganado", delta_color="inverse")

            tab_info, tab_receta = st.tabs(["📋 Manual Operativo", "🧮 Calculadora de Días de Ocupación"])

            with tab_info:
                st.error("🛑 **REGLA DE ORO:** El tiempo de ocupación en una parcela NUNCA debe superar los 3 días. Si las dejas más tiempo, la vaca se comerá el rebrote nuevo de la planta y la matará de raíz.")

                st.markdown("#### 🛠️ Pasos de Operación")
                st.write("1. **Medir (Aforo):** Corta un cuadrado de 1x1 metro de tu pasto y pésalo para saber cuánta comida hay.\n2. **Calcular:** Usa la pestaña de al lado para saber cuántos días les durará esa comida.\n3. **Mover:** Abre la puerta a la siguiente parcela antes de que el pasto quede a ras de suelo.\n4. **Descansar:** No regreses a las vacas a esa primera parcela hasta que el pasto vuelva a estar alto y maduro.")

            with tab_receta:
                st.markdown("#### 🧮 Calculadora de Capacidad de Carga")
                st.write("Calcula exactamente cuántos días puedes dejar a tu lote en un potrero sin destruir el pasto:")

                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    st.markdown("**1. Tu Ganado (Demanda)**")
                    peso_promedio_ph = st.number_input("Peso promedio por vaca (kg):", min_value=100, value=400, step=10)
                    cabezas_ph = st.number_input("Número de cabezas en el lote:", min_value=10, value=100, step=5)
                with col_c2:
                    st.markdown("**2. Tu Pasto (Oferta)**")
                    aforo_m2 = st.number_input("¿Cuánto pesa 1m² de tu pasto? (kg):", min_value=0.1, value=1.5, step=0.1, help="Corta 1 metro cuadrado de pasto a ras de suelo y pésalo.")
                    hectareas_potrero = st.number_input("Tamaño del potrero (Hectáreas):", min_value=1.0, value=2.0, step=0.5)
                with col_c3:
                    st.markdown("**3. Eficiencia**")
                    porcentaje_aprovechamiento = st.slider("Desperdicio (%):", min_value=30, max_value=80, value=50, help="El ganado pisotea y ensucia pasto. 50% significa que solo aprovechan la mitad de la comida.")

                res_prv = calcular_rotacion_prv(hectareas_potrero, aforo_m2, cabezas_ph, peso_promedio_ph, porcentaje_aprovechamiento)

                st.divider()
                st.subheader("📊 Veredicto de Rotación")
                col_r1, col_r2, col_r3 = st.columns(3)
                
                col_r1.metric("Comida Real Disponible", f"{res_prv['forraje_util_ton']:,.1f} Toneladas", "Ya descontando el pasto pisoteado")
                col_r2.metric("Consumo del Lote", f"{res_prv['consumo_diario_kg']:,.1f} kg / día", "Lo que tragan todos juntos en 24 hrs")
                
                if res_prv['dias_ocupacion'] > 3:
                    col_r3.metric("Límite de Ocupación", f"{res_prv['dias_ocupacion']:.1f} Días", "⚠️ Demasiado tiempo. Subdivide tu potrero.", delta_color="inverse")
                else:
                    col_r3.metric("Límite de Ocupación", f"{res_prv['dias_ocupacion']:.1f} Días", "✅ Rango perfecto de pastoreo.", delta_color="off")