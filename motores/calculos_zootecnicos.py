import pulp
import pandas as pd

def optimizar_dieta_pulp(base_datos, req_proteina, req_energia):
    """
    Motor matemático (PuLP) para optimizar dietas.
    Implementa el Punto 7: Verifica stock real en inventario.
    """
    # FILTRO DE INVENTARIO REAL 
    # Solo usar insumos con stock > 0
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

    # Restricciones de máximos 
    for i in insumos:
        if "max_pct" in insumos_disponibles[i]:
            prob += x[i] <= insumos_disponibles[i]["max_pct"], f"Max_{i}"

    # Restricciones de tóxicos
    toxicos = [i for i in ["urea_agricola", "pollinaza", "harina_pescado"] if i in insumos]
    if "urea_agricola" in toxicos: prob += x["urea_agricola"] <= 0.5, "Tope_Urea"
    if "pollinaza" in toxicos: prob += x["pollinaza"] <= 12.0, "Tope_Pollinaza"
    if "harina_pescado" in toxicos: prob += x["harina_pescado"] <= 4.0, "Tope_Pescado"
    if len(toxicos) >= 2: prob += pulp.lpSum([x[i] for i in toxicos]) <= 11.0, "Colchon_Paranoia_Palatabilidad"

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
        return {"exito": False, "error": "No hay suficientes insumos en stock para lograr esta mezcla. Compra ingredientes más proteicos o energéticos."}