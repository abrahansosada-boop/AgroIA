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