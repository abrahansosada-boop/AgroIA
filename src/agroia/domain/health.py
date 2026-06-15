def calcular_protocolo_sanitario(peso: float, datos_desp: dict = None, datos_vac: dict = None) -> dict:
    """Calcula las dosis, costos y tiempos de retiro del protocolo sanitario."""
    
    if not datos_desp:
        datos_desp = {"dosis_ml_por_kg": 0.0, "costo_por_ml": 0.0, "tiempo_retiro_dias": 0}
        
    if not datos_vac:
        datos_vac = {"dosis_ml_fija": 0.0, "costo_por_dosis": 0.0, "tiempo_retiro_dias": 0}

    dosis_exacta_ml_desp = peso * datos_desp.get("dosis_ml_por_kg", 0.0)
    costo_desp = dosis_exacta_ml_desp * datos_desp.get("costo_por_ml", 0.0)
    
    dosis_vac = datos_vac.get("dosis_ml_fija", 0.0)
    costo_vac = datos_vac.get("costo_por_dosis", 0.0)
    
    costo_salud_total = costo_desp + costo_vac
    retiro_dias = max(datos_desp.get("tiempo_retiro_dias", 0), datos_vac.get("tiempo_retiro_dias", 0))
    
    if retiro_dias > 0:
        mensaje_retiro = f"🛑 BLOQUEO COMERCIAL: Los animales NO pueden ir a rastro en los próximos {retiro_dias} días debido a residuos en tejidos."
        apto_venta = False
    else:
        mensaje_retiro = "✅ LIBRE DE RESIDUOS: Comercialización inmediata autorizada."
        apto_venta = True

    return {
        "dosis_desparasitante_ml": round(dosis_exacta_ml_desp, 2),
        "costo_desparasitante": round(costo_desp, 2),
        "dosis_vacuna_ml": round(dosis_vac, 2),
        "costo_vacuna": round(costo_vac, 2),
        "costo_total": round(costo_salud_total, 2),
        "dias_retiro": retiro_dias,
        "apto_para_venta": apto_venta,
        "mensaje_retiro": mensaje_retiro
    }

def calcular_meta_ganancia(proteina_mezcla: float) -> float:
    """Calcula la meta sugerida de ganancia diaria basada en la proteína de la dieta."""
    return round(0.8 + ((proteina_mezcla - 14.0) * 0.05), 2)


def evaluar_rendimiento_pesada(peso_anterior: float, peso_actual: float, dias: int, meta_ia: float) -> dict:
    """Calcula la ganancia diaria de peso (GDP) y evalúa el desempeño del lote o animal."""
    if dias <= 0:
        return {"exito": False, "error": "Los días transcurridos deben ser mayores a cero."}
    if peso_actual <= peso_anterior:
        return {"exito": False, "error": "El peso actual no puede ser menor o igual al anterior. Revisa los datos."}

    ganancia_total = peso_actual - peso_anterior
    gdp_real = ganancia_total / dias
    diferencia_meta = gdp_real - meta_ia

    if gdp_real >= meta_ia:
        estado = "EXCELENTE"
        mensaje = "El desempeño supera o iguala la proyección de la dieta. ¡Buen trabajo!"
    elif gdp_real >= meta_ia * 0.8:
        estado = "ALERTA"
        mensaje = "Están ganando peso, pero un poco por debajo de la meta. Revisa el consumo en comederos."
    else:
        estado = "PELIGRO"
        mensaje = "Los animales están estancados. Revisa sanidad, estrés por clima o corrige la dieta."

    return {
        "exito": True,
        "ganancia_total": ganancia_total,
        "gdp_real": gdp_real,
        "diferencia_meta": diferencia_meta,
        "estado": estado,
        "mensaje": mensaje
    }

def calcular_perdida_mortandad(bajas: int, vacunado: bool, costo_salud_unitario: float = 50.0) -> dict:
    """Calcula la fuga de capital por mortandad basándose en protocolos médicos aplicados."""
    if bajas <= 0:
        return {"exito": False, "error": "El número de bajas debe ser mayor a cero."}

    perdida_medica = (bajas * costo_salud_unitario) if vacunado else 0.0

    return {
        "exito": True,
        "perdida_medica": perdida_medica
    }