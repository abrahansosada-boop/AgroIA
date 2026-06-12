import streamlit as st
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
            ["🌵 Bio-Fábrica de Nopal Forrajero", "🌱 Cultivo Rústico de Azolla", "🌾 Enriquecimiento de Esquilmos (Silo de Tamo)"],
            horizontal=True
        )
        
        st.divider()
        
        # MODULO NOPAL FORRAJERO
        if "Nopal Forrajero" in tech_p1:
            st.markdown("### 🌵 Bio-Fábrica de Nopal Forrajero")
            st.caption("📍 Origen de validación: Zonas semiáridas y Nordeste Brasileño")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "BAJO", "Baja inversión de capital", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "EXCELENTE", "Disponibilidad de material vegetativo local", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "BAJA", "Requiere mano de obra estándar", delta_color="off")
            
            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Calculadora de Racionamiento AgroIA"])
            
            with tab_info:
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Déficit hídrico severo o ausencia de agua de bebida circulante.
                        * Escasez de forraje verde de alta energía en pastoreo.
                        * Estrategia de mantenimiento estacional para ganado bovino de cría.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * **RESTRICCIÓN:** No suministrar pencas de nopal de forma exclusiva. El exceso de agua libre y mucílago genera tránsito intestinal acelerado (diarrea mecánica), provocando deshidratación y pérdida de peso.
                        * **OBLIGATORIEDAD:** Integrar siempre una fuente de fibra larga seca (tamo, rastrojo o paja) para asegurar la rumia correcta.
                    """)
                
                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Cosecha:** Cortar pencas maduras (evitar brotes tiernos por exceso de acidez).
                    2. **Acondicionamiento:** Eliminar espinas mediante chamuscado rápido con quemador de gas.
                    3. **Procesamiento:** Picar en fragmentos de aproximadamente 3x3 cm para facilitar la prensión.
                    4. **Homogeneización:** Mezclar uniformemente con la fracción de fibra seca calculada en la pestaña contigua.
                """)
                
            with tab_receta:
                st.markdown("#### 🧮 Optimización de Dieta de Emergencia y Retorno de Inversión (ROI)")
                st.write("Determine los requerimientos diarios y evalúe el impacto financiero de la contingencia:")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    num_animales = st.number_input("Número de animales en el lote:", min_value=1, value=50, step=1)
                with col_c2:
                    peso_promedio = st.number_input("Peso vivo promedio (kg):", min_value=50, value=400, step=10)
                with col_c3:
                    dias_periodo = st.number_input("Días estimados de contingencia:", min_value=1, value=60, step=5)
                
                consumo_total_fresco_dia = peso_promedio * 0.10
                nopal_por_animal_dia = consumo_total_fresco_dia * 0.75
                tamo_por_animal_dia = consumo_total_fresco_dia * 0.25
                
                total_nopal_necesario = nopal_por_animal_dia * num_animales * dias_periodo
                total_tamo_necesario = tamo_por_animal_dia * num_animales * dias_periodo
                
                st.subheader("📊 Requerimientos Totales de Suministro")
                col_r1, col_r2 = st.columns(2)
                
                with col_r1:
                    st.info(f"🌵 **Nopal Forrajero requerido:**\n* **Por animal/día:** {nopal_por_animal_dia:.1f} kg\n* **Total Periodo:** {total_nopal_necesario / 1000:.2f} Toneladas")
                with col_r2:
                    st.success(f"🌾 **Tamo / Rastrojo requerido:**\n* **Por animal/día:** {tamo_por_animal_dia:.1f} kg\n* **Total Periodo:** {total_tamo_necesario / 1000:.2f} Toneladas")
                
                st.divider()
                
                # CALCULADORA ROI FINANCIERO NOPAL
                st.markdown("#### 💵 Impacto Financiero y Retorno Operativo")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    costo_ton_tamo = st.number_input("Costo de Tamo/Rastrojo por Tonelada ($):", min_value=100, value=1500, step=100)
                    
                    st.markdown("**🚜 Desglose Operativo (Extracción de Nopal)**")
                    jornal_diario = st.number_input("Pago diario al trabajador ($):", min_value=100, value=350, step=50)
                    gasto_gas_gasolina = st.number_input("Gasto diario en Gasolina/Gas LP ($):", min_value=0, value=150, step=50)
                    toneladas_dia = st.number_input("Toneladas recolectadas por día:", min_value=0.5, value=2.0, step=0.5)
                    
                    costo_corte_nopal = (jornal_diario + gasto_gas_gasolina) / toneladas_dia if toneladas_dia > 0 else 0
                    st.caption(f"Costo operativo automatizado: **${costo_corte_nopal:.2f} / Tonelada**")
                    
                with col_f2:
                    costo_ton_paca = st.number_input("Costo de Paca Comercial por Tonelada ($):", min_value=1000, value=5000, step=100)
                
                costo_total_resiliencia = ((total_nopal_necesario / 1000) * costo_corte_nopal) + ((total_tamo_necesario / 1000) * costo_ton_tamo)
                
                consumo_paca_dia = peso_promedio * 0.03
                total_paca_necesaria = consumo_paca_dia * num_animales * dias_periodo
                costo_total_tradicional = (total_paca_necesaria / 1000) * costo_ton_paca
                
                ahorro_generado = costo_total_tradicional - costo_total_resiliencia
                porcentaje_ahorro = (ahorro_generado / costo_total_tradicional) * 100 if costo_total_tradicional > 0 else 0
                
                st.markdown("##### 📈 Proyección de Ahorro Operativo")
                col_res1, col_res2, col_res3 = st.columns(3)
                col_res1.metric("Inversión Dieta Tradicional", f"${costo_total_tradicional:,.2f}", "Compra externa", delta_color="inverse")
                col_res2.metric("Inversión Nopal + Tamo", f"${costo_total_resiliencia:,.2f}", "Aprovechamiento local", delta_color="off")
                col_res3.metric("Capital Salvado (Ahorro)", f"${ahorro_generado:,.2f}", f"{porcentaje_ahorro:.1f}% reducción de costos")

        # MODULO AZOLLA
        elif "Azolla" in tech_p1:
            st.markdown("### 🌱 Cultivo Rústico de Azolla")
            st.caption("📍 Origen de validación: Sistemas intensivos de pequeña escala en India y Asia de bajos recursos")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "MUY BAJO", "Estructuras rústicas de lona", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "MEDIO", "Adquisición de cepa madre por canales comerciales", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "MEDIA", "Requiere monitoreo diario de calidad de agua", delta_color="off")
            
            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Calculadora de Área de Cultivo"])
            
            with tab_info:
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Sustitución parcial de fuentes de proteína comerciales caras (Alfalfa, Pasta de Soya).
                        * Suplementación proteica en ganado lechero estabulado o semi-estabulado.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS:**
                        * No permitir que la temperatura del agua exceda los 38°C; genera muerte térmica del helecho.
                        * Mantener un control estricto de la carga orgánica (estiércol utilizado como fertilizante) para evitar procesos de eutrofización y descomposición anaeróbica de la pileta.
                    """)
                    
                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("1. Excavación y nivelación de fosas de 2x2 metros. 2. Colocación de película plástica impermeable. 3. Incorporación de suelo franco y fuente de fósforo/estiércol diluido. 4. Cosecha del 30% de la biomasa cada 24 horas.")

            with tab_receta:
                st.markdown("#### 🧮 Dimensionamiento de Módulos Acuáticos")
                st.write("Determine el área de piletas requerida para su lote y evalúe la viabilidad económica:")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    num_vacas = st.number_input("Animales a suplementar:", min_value=1, value=20, step=1)
                with col_c2:
                    consumo_diario_azolla = st.number_input("Consumo Azolla Fresca (kg/animal/día):", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
                with col_c3:
                    rendimiento_m2 = st.number_input("Rendimiento estimado (kg/m²/día):", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
                
                produccion_diaria_requerida = num_vacas * consumo_diario_azolla
                area_necesaria_m2 = produccion_diaria_requerida / rendimiento_m2
                
                st.subheader("📐 Requerimientos de Infraestructura")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.info(f"💧 **Área Activa de Cultivo:** {area_necesaria_m2:.1f} m²\n\n*Equivalente a {int(area_necesaria_m2/4) + 1} piletas estándar de 2x2 metros.*")
                with col_r2:
                    st.success(f"🌿 **Producción Diaria de Biomasa:** {produccion_diaria_requerida:.1f} kg frescos.")
                    
                st.divider()
                
                # CALCULADORA ROI FINANCIERO AZOLLA
                st.markdown("#### 💵 Impacto Financiero y Sustitución de Proteína")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    costo_kg_azolla = st.number_input("Costo operativo Azolla (kg fresco) [$]:", min_value=0.1, value=0.50, step=0.1, help="Considera agua, mano de obra y fertilizante.")
                with col_f2:
                    costo_kg_comercial = st.number_input("Costo Suplemento Comercial Sustituido (kg) [$]:", min_value=1.0, value=6.0, step=0.5, help="Costo del concentrado proteico equivalente.")
                
                gasto_diario_azolla = produccion_diaria_requerida * costo_kg_azolla
                gasto_diario_comercial = produccion_diaria_requerida * costo_kg_comercial
                ahorro_diario_azolla = gasto_diario_comercial - gasto_diario_azolla
                ahorro_anual_azolla = ahorro_diario_azolla * 365
                
                st.markdown("##### 📈 Proyección de Ahorro Anualizado")
                col_res1, col_res2, col_res3 = st.columns(3)
                col_res1.metric("Gasto Anual Comercial", f"${(gasto_diario_comercial * 365):,.2f}", delta_color="inverse")
                col_res2.metric("Gasto Anual Azolla", f"${(gasto_diario_azolla * 365):,.2f}", delta_color="off")
                col_res3.metric("Ahorro Neto Anualizado", f"${ahorro_anual_azolla:,.2f}", "Retención de flujo de caja")

        # MODULO SILO DE TAMO
        elif "Silo de Tamo" in tech_p1:
            st.markdown("### 🌾 Enriquecimiento de Esquilmos (Silo de Tamo)")
            st.caption("📍 Origen de validación: Sistemas de optimización de rastrojos a nivel global")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("💰 Costo de Implementación", "BAJO", "Aprovechamiento de subproductos", delta_color="normal")
            col_v2.metric("🇲🇽 Acceso en México", "ALTO", "Insumos base disponibles", delta_color="normal")
            col_v3.metric("🧠 Complejidad Operativa", "ALTA", "Requiere precisión en dosificación", delta_color="inverse")
            
            tab_info, tab_receta = st.tabs(["📋 Manual Operativo y Seguridad", "🧮 Calculadora de Enriquecimiento y ROI"])
            
            with tab_info:
                col_ind, col_contra = st.columns(2)
                with col_ind:
                    st.success("""
                        **🎯 INDICACIONES DE USO:**
                        * Conversión de forrajes de muy baja calidad (paja, rastrojo, tamo) en alimento de mantenimiento.
                        * Reducción de costos de alimentación invernal o en estiaje severo.
                        * Incremento de digestibilidad y proteína cruda en biomasa seca.
                    """)
                with col_contra:
                    st.error("""
                        **🛑 CONTRAINDICACIONES Y ALERTAS (CRÍTICO):**
                        * **INTOXICACIÓN POR UREA:** Una mala disolución o aplicación heterogénea causará concentración de nitrógeno letal para el bovino.
                        * **BOTULISMO Y HONGOS:** Una compactación deficiente o ruptura del sello plástico (entrada de oxígeno) pudrirá el silo. Desechar cualquier capa negra o con moho.
                    """)
                    
                st.markdown("#### 🛠️ Procedimiento Operativo Estándar (SOP)")
                st.info("""
                    1. **Preparación:** Picar el rastrojo o tamo a un tamaño aproximado de 5 cm.
                    2. **Mezcla Líquida:** Disolver perfectamente la urea y la melaza en el agua estipulada. No deben quedar grumos ni residuos sólidos.
                    3. **Estratificación:** Extender el tamo en capas de 20 cm sobre una superficie limpia o trinchera.
                    4. **Asperjado y Compactado:** Rociar la mezcla líquida uniformemente sobre cada capa y compactar (con tractor o rodillo) para expulsar el aire.
                    5. **Sellado Anaeróbico:** Cubrir herméticamente con lona plástica y sellar bordes con tierra. Fermentar por un mínimo de 21 días antes de abrir.
                """)

            with tab_receta:
                st.markdown("#### 🧮 Dosificación Estructural de Amonificación")
                st.write("Determine los volúmenes de formulación requeridos para su inventario:")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    num_vacas_silo = st.number_input("Número de animales:", min_value=1, value=50, step=1, key="num_vacas_silo")
                with col_c2:
                    peso_promedio_silo = st.number_input("Peso vivo promedio (kg):", min_value=50, value=400, step=10, key="peso_silo")
                with col_c3:
                    dias_silo = st.number_input("Días de contingencia a cubrir:", min_value=1, value=60, step=5, key="dias_silo")
                
                consumo_ms_dia = peso_promedio_silo * 0.025
                total_tamo_base = consumo_ms_dia * num_vacas_silo * dias_silo
                
                factor_ton = total_tamo_base / 1000
                total_urea = factor_ton * 50
                total_melaza = factor_ton * 100
                total_agua = factor_ton * 300
                
                st.subheader("📊 Formulación Exacta del Silo")
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("🌾 Tamo/Rastrojo Seco", f"{total_tamo_base:,.1f} kg")
                col_r2.metric("🧪 Urea Agrícola/Pecuaria", f"{total_urea:,.1f} kg")
                col_r3.metric("🍯 Melaza y 💧 Agua", f"{total_melaza:,.1f} kg / {total_agua:,.1f} L")
                
                st.divider()
                
                # CALCULADORA ROI FINANCIERO SILO
                st.markdown("#### 💵 Impacto Financiero y Retorno Operativo")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    costo_tamo_base = st.number_input("Costo Tamo Seco (Ton) [$]:", min_value=100.0, value=float(base_datos.get("rastrojo_maiz", {}).get("costo_kg", 1.5) * 1000), step=100.0, key="costo_tamo_silo_unico")
                    costo_urea = st.number_input("Costo Urea (kg) [$]:", min_value=1.0, value=float(base_datos.get("urea_agricola", {}).get("costo_kg", 12.0)), step=1.0, key="costo_urea_silo_unico")
                    costo_melaza = st.number_input("Costo Melaza (kg) [$]:", min_value=1.0, value=float(base_datos.get("melaza_cana", {}).get("costo_kg", 6.0)), step=1.0, key="costo_melaza_silo_unico")
                with col_f2:
                    costo_paca_comercial = st.number_input("Costo Paca Calidad Media (Ton) [$]:", min_value=1000, value=4500, step=100, key="costo_paca_silo_unico")
                
                costo_total_insumos_silo = (factor_ton * costo_tamo_base) + (total_urea * costo_urea) + (total_melaza * costo_melaza)
                costo_total_paca = factor_ton * costo_paca_comercial
                
                ahorro_silo = costo_total_paca - costo_total_insumos_silo
                porcentaje_ahorro_silo = (ahorro_silo / costo_total_paca) * 100 if costo_total_paca > 0 else 0
                
                st.markdown("##### 📈 Proyección de Ahorro en Alimentación Base")
                col_res1, col_res2, col_res3 = st.columns(3)
                col_res1.metric("Costo Equivalente Pacas", f"${costo_total_paca:,.2f}", delta_color="inverse")
                col_res2.metric("Costo Producción Silo", f"${costo_total_insumos_silo:,.2f}", delta_color="off")
                col_res3.metric("Capital Salvado", f"${ahorro_silo:,.2f}", f"{porcentaje_ahorro_silo:.1f}% de reducción")

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
                    hectareas_disponibles = st.number_input("Hectáreas del potrero a sembrar:", min_value=1.0, value=10.0, step=1.0)
                    carga_actual = st.number_input("Carga animal actual (Vacas/Hectárea):", min_value=0.1, value=1.0, step=0.1)
                with col_c2:
                    multiplicador_sspi = st.slider("Multiplicador de biomasa esperado:", min_value=1.5, max_value=5.0, value=3.0, step=0.5)
                    valor_vaca_promedio = st.number_input("Valor comercial promedio por vaca ($):", min_value=5000, value=25000, step=1000)

                carga_proyectada = carga_actual * multiplicador_sspi
                vacas_actuales_totales = hectareas_disponibles * carga_actual
                vacas_nuevas_totales = hectareas_disponibles * carga_proyectada
                incremento_vacas = vacas_nuevas_totales - vacas_actuales_totales

                valor_capital_adicional = incremento_vacas * valor_vaca_promedio

                st.subheader("📊 Nuevo Límite Biológico del Rancho")
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Carga Actual (Total)", f"{vacas_actuales_totales:.0f} Cabezas")
                col_r2.metric("Nueva Carga SSPi", f"{vacas_nuevas_totales:.0f} Cabezas", f"+{incremento_vacas:.0f} espacios nuevos")
                col_r3.metric("Densidad Operativa", f"{carga_proyectada:.1f} Vacas/Ha")

                st.divider()
                st.markdown("##### 💵 Valorización de Activos Biológicos")
                st.metric("Incremento de Capital Soportado", f"${valor_capital_adicional:,.2f} MXN", "Capacidad extra del rancho valorizada en ganado")

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
                    num_vacas_boma = st.number_input("Número de cabezas a confinar:", min_value=10, value=100, step=10)
                with col_c2:
                    peso_promedio_boma = st.number_input("Peso promedio por animal (kg):", min_value=100, value=400, step=10)

                peso_total_hato = num_vacas_boma * peso_promedio_boma
                ugm_totales = peso_total_hato / 500
                area_boma_m2 = ugm_totales * 3.0
                perimetro_metros = 4 * (area_boma_m2 ** 0.5)

                st.subheader("📐 Especificaciones Estructurales")
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("Área Requerida", f"{area_boma_m2:.1f} m²", "Confinamiento de alta densidad")
                col_r2.metric("Perímetro de Cerco", f"{perimetro_metros:.1f} metros lineales", "Diseño cuadrangular")

                st.divider()

                st.markdown("##### 💵 Ahorro Equivalente en Agroquímicos")
                
                excretas_frescas_noche = (peso_total_hato * 0.08) / 2
                nitrogeno_puro_kg = excretas_frescas_noche * 0.005 
                urea_equivalente_kg = nitrogeno_puro_kg * 2.17 

                # Reemplaza la línea del input de urea (433 o 448 según cual dejes):
                costo_urea_kg = st.number_input("Precio de la Urea Química ($/kg):", min_value=1.0, value=float(base_datos.get("urea_agricola", {}).get("costo_kg", 15.0)), step=1.0, key="costo_urea_boma")
                ahorro_fertilizante_diario = urea_equivalente_kg * costo_urea_kg

                col_f1, col_f2 = st.columns(2)
                col_f1.metric("Estiércol y Orina", f"{excretas_frescas_noche:,.1f} kg / noche")
                col_f2.metric("Ahorro Operativo", f"${ahorro_fertilizante_diario:,.2f} / noche", f"Equivalente a {urea_equivalente_kg:.1f} kg de Urea")

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

                inversion_cerco_fisico = km_cerco_evitados * costo_km_cerco
                inversion_collares = cabezas_a_equipar * costo_collar_unitario
                ahorro_infraestructura = inversion_cerco_fisico - inversion_collares
                
                st.subheader("📊 Diagnóstico de Retorno de Inversión")
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Gasto en Cerco Físico", f"${inversion_cerco_fisico:,.2f}", delta_color="inverse")
                col_r2.metric("Inversión en Collares", f"${inversion_collares:,.2f}", delta_color="off")
                
                if ahorro_infraestructura > 0:
                    col_r3.metric("Capital a Favor", f"${ahorro_infraestructura:,.2f}", "Punto de equilibrio superado")
                else:
                    col_r3.metric("Déficit de Inversión", f"${ahorro_infraestructura:,.2f}", "Costo de hardware excede infraestructura", delta_color="inverse")

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

                consumo_diario_hato = cabezas_ph * (peso_promedio_ph * 0.10) 
                forraje_total_verde = (aforo_m2 * 10000) * hectareas_potrero
                forraje_util = forraje_total_verde * (porcentaje_aprovechamiento / 100)
                
                dias_ocupacion = forraje_util / consumo_diario_hato if consumo_diario_hato > 0 else 0

                st.divider()
                st.subheader("📊 Veredicto de Rotación")
                col_r1, col_r2, col_r3 = st.columns(3)
                
                col_r1.metric("Comida Real Disponible", f"{forraje_util / 1000:,.1f} Toneladas", "Ya descontando el pasto pisoteado")
                col_r2.metric("Consumo del Lote", f"{consumo_diario_hato:,.1f} kg / día", "Lo que tragan todos juntos en 24 hrs")
                
                if dias_ocupacion > 3:
                    col_r3.metric("Límite de Ocupación", f"{dias_ocupacion:.1f} Días", "⚠️ Demasiado tiempo. Subdivide tu potrero.", delta_color="inverse")
                else:
                    col_r3.metric("Límite de Ocupación", f"{dias_ocupacion:.1f} Días", "✅ Rango perfecto de pastoreo.", delta_color="off")
