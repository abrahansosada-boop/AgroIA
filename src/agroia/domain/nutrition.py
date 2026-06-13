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