import pulp
import pandas as pd

def calcular_correccion_pearson(prot_actual: float, kilos_tolva: float, prot_objetivo: float, prot_refuerzo: float) -> dict:
    """Calcula los kilos exactos para corregir una mezcla usando el Cuadrado de Pearson."""
    if prot_objetivo <= prot_actual or prot_objetivo >= prot_refuerzo:
        return {"exito": False, "error": "La proteína objetivo debe estar ENTRE la actual y la del refuerzo."}
    
    partes_refuerzo = abs(prot_objetivo - prot_actual)
    partes_mezcla = abs(prot_refuerzo - prot_objetivo)
    kilos_a_anadir = (kilos_tolva / partes_mezcla) * partes_refuerzo
    
    return {"exito": True, "kilos_a_anadir": kilos_a_anadir}


def auditar_mezcla_manual(ingredientes_mezcla: list) -> dict:
    """Evalúa los aportes nutricionales de una mezcla ingresada a mano."""
    total_kilos = sum(item["kilos"] for item in ingredientes_mezcla)
    
    if total_kilos <= 0:
        return {"exito": False, "error": "Agregue kilos a los ingredientes."}
        
    prot_acum = sum((item["kilos"] * item["datos"].get("proteina_pct", 0)) for item in ingredientes_mezcla) / total_kilos
    ener_acum = sum((item["kilos"] * item["datos"].get("energia_mcal", 0)) for item in ingredientes_mezcla) / total_kilos
    fibr_acum = sum((item["kilos"] * item["datos"].get("fibra_pct", 0)) for item in ingredientes_mezcla) / total_kilos
    costo_tot = sum((item["kilos"] * item["datos"].get("costo_kg", 0)) for item in ingredientes_mezcla)
    
    return {
        "exito": True,
        "total_kilos": total_kilos,
        "proteina": prot_acum,
        "energia": ener_acum,
        "fibra": fibr_acum,
        "costo_total": costo_tot,
        "costo_kg": costo_tot / total_kilos
    }


def optimizar_dieta_pulp(base_datos: dict, req_proteina: float, req_energia: float) -> dict:
    """
    Motor matemático (PuLP) para optimizar dietas.
    Implementa el Punto 7: Verifica stock real en inventario y minimiza costos.
    """
    # FILTRO DE INVENTARIO REAL: Solo usar insumos con stock > 0
    insumos_disponibles = {
        insumo: datos for insumo, datos in base_datos.items() 
        if datos.get("stock_kg", 0) > 0
    }

    if not insumos_disponibles:
        return {"exito": False, "error": "Tu bodega está vacía o sin stock en ningún insumo. Ve a comprar inventario."}
        
    if len(insumos_disponibles) < 2:
        return {"exito": False, "error": "Necesitas al menos 2 ingredientes con stock para poder hacer una mezcla."}

    insumos = list(insumos_disponibles.keys())
    prob = pulp.LpProblem("Dieta_Barata", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("Ingrediente", insumos, lowBound=0)

    # Función objetivo: Minimizar costo
    prob += pulp.lpSum([x[i] * insumos_disponibles[i]["costo_kg"] for i in insumos]), "Costo"
    
    # Restricciones base
    prob += pulp.lpSum([x[i] for i in insumos]) == 100, "Peso_100"
    prob += pulp.lpSum([x[i] * insumos_disponibles[i]["proteina_pct"] for i in insumos]) >= req_proteina * 100, "Req_Prot"
    prob += pulp.lpSum([x[i] * insumos_disponibles[i]["energia_mcal"] for i in insumos]) >= req_energia * 100, "Req_Ener"

    # Restricciones de palatabilidad (max_pct) definidos en la base de datos
    for i in insumos:
        if "max_pct" in insumos_disponibles[i]:
            prob += x[i] <= insumos_disponibles[i]["max_pct"], f"Max_{i}"

    # FILTROS DE TOXICIDAD Y RESTRICCIONES BIOLÓGICAS
    toxicos = [i for i in ["urea_agricola", "pollinaza", "harina_pescado", "harina_hueso"] if i in insumos]
    
    if "urea_agricola" in toxicos: prob += x["urea_agricola"] <= 0.5, "Tope_Urea"
    if "pollinaza" in toxicos: prob += x["pollinaza"] <= 12.0, "Tope_Pollinaza"
    if "harina_pescado" in toxicos: prob += x["harina_pescado"] <= 4.0, "Tope_Pescado"
    if "harina_hueso" in toxicos: prob += x["harina_hueso"] <= 1.5, "Tope_Hueso" # Límite de toxicidad mineral
    
    # Colchón de paranoia: Si la IA intenta usar mucha basura junta para abaratar, la frenamos.
    if len(toxicos) >= 2: 
        prob += pulp.lpSum([x[i] for i in toxicos]) <= 11.0, "Colchon_Paranoia_Palatabilidad"

    prob.solve(pulp.PULP_CBC_CMD(msg=False)) 

    if pulp.LpStatus[prob.status] == "Optimal":
        resultados = []
        costo_cien_kg = 0
        detalles_kilos = {}
        ingredientes_usados = []

        for i in insumos:
            if x[i].varValue > 0.01:
                costo_ing = x[i].varValue * insumos_disponibles[i]["costo_kg"]
                costo_cien_kg += costo_ing
                
                resultados.append({
                    "Insumo": i.upper(), 
                    "Kilos por 100kg": round(x[i].varValue, 2),
                    "Costo ($)": round(costo_ing, 2)
                })
                ingredientes_usados.append(i)
                detalles_kilos[i] = float(x[i].varValue)

        return {
            "exito": True,
            "df": pd.DataFrame(resultados),
            "costo_kg": costo_cien_kg / 100,
            "detalles_ia": {"ingredientes": ingredientes_usados, "kilos": detalles_kilos},
            "proteina_log": req_proteina, 
            "energia_log": req_energia
        }
    else:
        return {"exito": False, "error": "No hay suficientes insumos proteicos o energéticos en la bodega para lograr esta mezcla. La IA no pudo resolverlo."}

def calcular_rendimiento_nopal(densidad_ha: int, peso_penca: float, pencas_por_planta: int) -> float:
    rendimiento_kg = densidad_ha * pencas_por_planta * peso_penca
    return rendimiento_kg / 1000.0


def calcular_rotacion_prv(hectareas: float, aforo_m2: float, cabezas: int, peso_promedio: float, porcentaje_aprovechamiento: float) -> dict:
    consumo_diario_hato = cabezas * (peso_promedio * 0.10)
    forraje_total_verde = (aforo_m2 * 10000.0) * hectareas
    forraje_util = forraje_total_verde * (porcentaje_aprovechamiento / 100.0)
    
    dias_ocupacion = forraje_util / consumo_diario_hato if consumo_diario_hato > 0 else 0.0

    return {
        "forraje_util_ton": forraje_util / 1000.0,
        "consumo_diario_kg": consumo_diario_hato,
        "dias_ocupacion": dias_ocupacion
    }
def calcular_biomasa_azolla(espejos_agua: int, m2_espejo: float, cosecha_m2: float, dias_cosecha: int) -> dict:
    """Calcula la biomasa de la Azolla por ciclo y su proyección anual."""
    if dias_cosecha <= 0:
        return {"ciclo_kg": 0.0, "anual_ton": 0.0}
        
    produccion_ciclo = espejos_agua * m2_espejo * cosecha_m2
    produccion_anual_kg = produccion_ciclo * (365 / dias_cosecha)
    
    return {
        "ciclo_kg": produccion_ciclo,
        "anual_ton": produccion_anual_kg / 1000.0
    }

def calcular_enriquecimiento_esquilmos(toneladas: float, precio_ton: float, tipo_tratamiento: str) -> dict:
    """Calcula los costos y el aumento de proteína de tratar esquilmos agrícolas."""
    tratamientos = {
        "Urea y Melaza": {"costo_extra": 450.0, "inc_pc": 4.0},
        "Amonificación": {"costo_extra": 600.0, "inc_pc": 6.0},
        "Inoculación de Hongos (Pleurotus)": {"costo_extra": 800.0, "inc_pc": 8.0}
    }
    
    datos = tratamientos.get(tipo_tratamiento, {"costo_extra": 0.0, "inc_pc": 0.0})
    
    costo_base_total = toneladas * precio_ton
    costo_tratamiento_total = toneladas * datos["costo_extra"]
    costo_final_total = costo_base_total + costo_tratamiento_total
    
    costo_final_ton = costo_final_total / toneladas if toneladas > 0 else 0.0
    
    return {
        "costo_final_ton": costo_final_ton,
        "incremento_pc": datos["inc_pc"],
        "costo_total": costo_final_total
    }

def calcular_silo_tamo(toneladas_tamo: float, precio_ton_tamo: float, litros_melaza_ton: float, precio_litro_melaza: float, litros_agua_ton: float) -> dict:
    if toneladas_tamo <= 0:
        return {"agua_requerida_lts": 0.0, "peso_final_ton": 0.0, "costo_ton_ensilada": 0.0, "costo_total": 0.0}

    kilos_tamo = toneladas_tamo * 1000.0
    agua_litros = toneladas_tamo * litros_agua_ton
    melaza_total = toneladas_tamo * litros_melaza_ton
    
    peso_final_ton = (kilos_tamo + agua_litros + melaza_total) / 1000.0
    
    costo_tamo_total = toneladas_tamo * precio_ton_tamo
    costo_melaza_total = melaza_total * precio_litro_melaza  
    costo_total = costo_tamo_total + costo_melaza_total
    
    return {
        "agua_requerida_lts": agua_litros,
        "peso_final_ton": peso_final_ton,
        "costo_total": costo_total,
        "costo_ton_ensilada": costo_total / peso_final_ton if peso_final_ton > 0 else 0.0
    }

def calcular_proyeccion_sspi(hectareas: float, carga_actual: float, multiplicador: float, valor_vaca: float) -> dict:
    """Calcula el incremento de capacidad y valorización de activos biológicos con SSPi."""
    carga_proyectada = carga_actual * multiplicador
    vacas_actuales = hectareas * carga_actual
    vacas_nuevas = hectareas * carga_proyectada
    incremento = vacas_nuevas - vacas_actuales
    
    return {
        "carga_proyectada": carga_proyectada,
        "vacas_actuales_totales": vacas_actuales,
        "vacas_nuevas_totales": vacas_nuevas,
        "incremento_vacas": incremento,
        "valor_capital_adicional": incremento * valor_vaca
    }


def calcular_efecto_boma(num_cabezas: int, peso_promedio: float, costo_urea_kg: float) -> dict:
    """Calcula los requerimientos físicos y el impacto biológico/financiero del Efecto Boma."""
    peso_total_hato = num_cabezas * peso_promedio
    ugm_totales = peso_total_hato / 500.0  
    area_m2 = ugm_totales * 3.0
    
    perimetro_m = 4 * (area_m2 ** 0.5) if area_m2 > 0 else 0.0
    
    excretas_noche = (peso_total_hato * 0.08) / 2
    nitrogeno_puro = excretas_noche * 0.005
    urea_eq = nitrogeno_puro * 2.17
    ahorro_financiero = urea_eq * costo_urea_kg
    
    return {
        "area_m2": area_m2,
        "perimetro_metros": perimetro_m,
        "excretas_noche_kg": excretas_noche,
        "urea_equivalente_kg": urea_eq,
        "ahorro_diario": ahorro_financiero
    }

def calcular_roi_cercos_virtuales(km_cerco_evitados: float, costo_km_cerco: float, cabezas_a_equipar: int, costo_collar_unitario: float) -> dict:
    """
    Calcula el impacto financiero comparativo entre levantar cercos físicos 
    tradicionales versus implementar collares GPS con cercados virtuales.
    """
    inversion_cerco_fisico = km_cerco_evitados * costo_km_cerco
    inversion_collares = cabezas_a_equipar * costo_collar_unitario
    ahorro = inversion_cerco_fisico - inversion_collares
    
    return {
        "inversion_cerco_fisico": inversion_cerco_fisico,
        "inversion_collares": inversion_collares,
        "ahorro_infraestructura": ahorro
    }