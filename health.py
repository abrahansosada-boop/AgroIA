def calcular_protocolo_sanitario(peso: float, datos_desp: dict = None, datos_vac: dict = None) -> dict:
    """
    Calcula dosis y costos utilizando Farmacocinética real (mg/kg) 
    y evalúa los tiempos de retiro para activar el Muro de Cuarentena Automático.
    """
    if not datos_desp:
        datos_desp = {}
        
    if not datos_vac:
        datos_vac = {}

    # 1. FARMACOCINÉTICA (Fármacos metabólicos, antibióticos, desparasitantes)
    dosis_exacta_ml_desp = 0.0
    if "dosis_base_mg_kg" in datos_desp and "concentracion_mg_ml" in datos_desp:
        # Ecuación QFB: (Peso * Dosis biológica) / Concentración del frasco
        dosis_exacta_ml_desp = (peso * datos_desp["dosis_base_mg_kg"]) / datos_desp["concentracion_mg_ml"]
    elif "dosis_ml_por_kg" in datos_desp: 
        # Fallback de seguridad por si en la interfaz ingresan un medicamento viejo
        dosis_exacta_ml_desp = peso * datos_desp["dosis_ml_por_kg"]
        
    costo_desp = dosis_exacta_ml_desp * datos_desp.get("costo_estimado_ml", datos_desp.get("costo_por_ml", 0.0))
    via_desp = datos_desp.get("via_administracion", "No especificada")

    # 2. DOSIFICACIÓN DE BIOLÓGICOS (Vacunas - Dosis Fija)
    dosis_vac = datos_vac.get("dosis_fija_ml", 0.0)
    costo_vac = datos_vac.get("costo_estimado_dosis", datos_vac.get("costo_por_dosis", 0.0))
    via_vac = datos_vac.get("via_administracion", "No especificada")
    
    # 3. IMPACTO FINANCIERO Y DEFENSA LEGAL (SENASICA)
    costo_salud_total = costo_desp + costo_vac
    retiro_dias = max(datos_desp.get("tiempo_retiro_dias", 0), datos_vac.get("tiempo_retiro_dias", 0))
    
    if retiro_dias > 0:
        mensaje_retiro = f"🛑 BLOQUEO COMERCIAL: Los animales NO pueden ir a rastro en los próximos {retiro_dias} días debido a residuos tóxicos."
        apto_venta = False
    else:
        mensaje_retiro = "✅ LIBRE DE RESIDUOS: Comercialización inmediata autorizada."
        apto_venta = True

    return {
        "dosis_desparasitante_ml": round(dosis_exacta_ml_desp, 2),
        "via_desparasitante": via_desp,
        "costo_desparasitante": round(costo_desp, 2),
        "dosis_vacuna_ml": round(dosis_vac, 2),
        "via_vacuna": via_vac,
        "costo_vacuna": round(costo_vac, 2),
        "costo_total": round(costo_salud_total, 2),
        "dias_retiro": retiro_dias,
        "apto_para_venta": apto_venta,
        "mensaje_retiro": mensaje_retiro
    }


def calcular_meta_ganancia(proteina_mezcla: float) -> float:
    """Calcula la meta biológica sugerida de ganancia diaria basada en la proteína bruta de la dieta."""
    return round(0.8 + ((proteina_mezcla - 14.0) * 0.05), 2)


def evaluar_rendimiento_pesada(peso_anterior: float, peso_actual: float, dias: int, meta_ia: float) -> dict:
    """Calcula la ganancia diaria de peso (GDP) y evalúa la conversión alimenticia metabólica del lote."""
    if dias <= 0:
        return {"exito": False, "error": "Los días transcurridos deben ser mayores a cero."}
    if peso_actual <= peso_anterior:
        return {"exito": False, "error": "El peso actual no puede ser menor o igual al anterior. Posible catabolismo muscular en curso."}

    ganancia_total = peso_actual - peso_anterior
    gdp_real = ganancia_total / dias
    diferencia_meta = gdp_real - meta_ia

    if gdp_real >= meta_ia:
        estado = "EXCELENTE"
        mensaje = "El desempeño biológico supera la proyección. Conversión alimenticia óptima."
    elif gdp_real >= meta_ia * 0.8:
        estado = "ALERTA"
        mensaje = "Sub-desempeño leve. Revisa el consumo de materia seca (IMS) en comederos o estrés térmico."
    else:
        estado = "PELIGRO"
        mensaje = "Estancamiento grave. Urgente: Auditar sanidad (carga parasitaria), acidosis subclínica o calidad de agua."

    return {
        "exito": True,
        "ganancia_total": ganancia_total,
        "gdp_real": gdp_real,
        "diferencia_meta": diferencia_meta,
        "estado": estado,
        "mensaje": mensaje
    }