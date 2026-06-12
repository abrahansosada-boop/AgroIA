def evaluar_riesgo_termico(raza: str, temperatura: float) -> dict:
    """Evalúa el riesgo de estrés calórico utilizando el codex genético oficial del rancho."""
    raza = raza.lower().strip()
    
    codex_genetico = {
        # BOS INDICUS
        "brahman": {"sangre": "Indicus", "clima": "Trópico/Calor Extremo", "riesgo_termico": "Nulo", "proposito": "Carne"},
        "nelore": {"sangre": "Indicus", "clima": "Trópico/Calor Extremo", "riesgo_termico": "Nulo", "proposito": "Carne"},
        "sardo negro": {"sangre": "Indicus", "clima": "Trópico/Humedad", "riesgo_termico": "Nulo", "proposito": "Doble Propósito"},
        "gyr": {"sangre": "Indicus", "clima": "Trópico/Calor", "riesgo_termico": "Nulo", "proposito": "Leche Tropical"},
        "indubrasil": {"sangre": "Indicus", "clima": "Trópico", "riesgo_termico": "Nulo", "proposito": "Carne"},
        "guzerat": {"sangre": "Indicus", "clima": "Trópico/Árido", "riesgo_termico": "Nulo", "proposito": "Doble Propósito"},
        
        # BOS TAURUS
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

    datos_raza = codex_genetico.get(raza, {"sangre": "Desconocida", "clima": "Variable", "riesgo_termico": "Desconocido", "proposito": "General"})
    
    riesgo = False
    mensaje = f"✅ CLIMA CONFORTABLE: Temperatura de {temperatura}°C dentro del rango de confort para su perfil."
    limite_termico = 30.0 
    
    if temperatura >= 35 and datos_raza["riesgo_termico"] in ["Crítico (>30°C)", "Crítico (>28°C)"]:
        riesgo = True
        limite_termico = 28.0 if "28" in datos_raza["riesgo_termico"] else 30.0
        mensaje = f"❌ INCOMPATIBILIDAD GRAVE: Un animal {datos_raza['sangre']} a {temperatura}°C sufrirá estrés térmico severo."
        
    elif temperatura >= 30 and datos_raza["riesgo_termico"] == "Alto":
        riesgo = True
        limite_termico = 30.0
        mensaje = f"⚠️ RIESGO MODERADO: La temperatura de {temperatura}°C está en el límite para esta genética."
        
    elif datos_raza["riesgo_termico"] == "Nulo":
        riesgo = False
        limite_termico = 35.0
        mensaje = f"✅ ADAPTABILIDAD PERFECTA: Genética resistente. Soporta bien los {temperatura}°C."

    return {
        "raza_detectada": raza.title(),
        "tipo_genetico": datos_raza["sangre"],
        "limite_termico": limite_termico,
        "temperatura_actual": temperatura,
        "riesgo_termico": riesgo,
        "mensaje": mensaje
    }