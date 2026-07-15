import re
from typing import Dict, Any

CODEX_METABOLICO: Dict[str, Dict[str, Any]] = {
    # --- BOS INDICUS PUROS
    "brahman": {"biotipo_metabolico": "INDICUS_FIBRAL_RUSTICO", "proporcion_indicus": 1.0, "factor_mantenimiento_enm": 0.88, "ingesta_materia_seca_max_pct": 2.5, "indice_reciclaje_urea_saliva": 1.30, "tasa_paso_ruminal": "Lenta", "umbral_termico_confort_c": 35.0},
    "nelore": {"biotipo_metabolico": "INDICUS_FIBRAL_RUSTICO", "proporcion_indicus": 1.0, "factor_mantenimiento_enm": 0.88, "ingesta_materia_seca_max_pct": 2.5, "indice_reciclaje_urea_saliva": 1.30, "tasa_paso_ruminal": "Lenta", "umbral_termico_confort_c": 36.0},
    "indubrasil": {"biotipo_metabolico": "INDICUS_FIBRAL_RUSTICO", "proporcion_indicus": 1.0, "factor_mantenimiento_enm": 0.90, "ingesta_materia_seca_max_pct": 2.6, "indice_reciclaje_urea_saliva": 1.25, "tasa_paso_ruminal": "Lenta", "umbral_termico_confort_c": 34.0},
    "guzerat": {"biotipo_metabolico": "INDICUS_FIBRAL_RUSTICO", "proporcion_indicus": 1.0, "factor_mantenimiento_enm": 0.88, "ingesta_materia_seca_max_pct": 2.55, "indice_reciclaje_urea_saliva": 1.30, "tasa_paso_ruminal": "Lenta", "umbral_termico_confort_c": 35.0},
    "sardo_negro": {"biotipo_metabolico": "INDICUS_LECHE_TROPICAL", "proporcion_indicus": 1.0, "factor_mantenimiento_enm": 0.89, "ingesta_materia_seca_max_pct": 2.55, "indice_reciclaje_urea_saliva": 1.30, "tasa_paso_ruminal": "Media", "umbral_termico_confort_c": 35.0},
    "gyr": {"biotipo_metabolico": "INDICUS_LECHE_TROPICAL", "proporcion_indicus": 1.0, "factor_mantenimiento_enm": 0.89, "ingesta_materia_seca_max_pct": 2.6, "indice_reciclaje_urea_saliva": 1.35, "tasa_paso_ruminal": "Media", "umbral_termico_confort_c": 34.0},

    # --- BOS TAURUS PUROS
    "angus": {"biotipo_metabolico": "TAURUS_METABOLISMO_ACELERADO", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 1.00, "ingesta_materia_seca_max_pct": 2.8, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Rapida", "umbral_termico_confort_c": 27.0},
    "hereford": {"biotipo_metabolico": "TAURUS_METABOLISMO_ACELERADO", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 0.98, "ingesta_materia_seca_max_pct": 2.75, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Rapida", "umbral_termico_confort_c": 28.0},
    "charolais": {"biotipo_metabolico": "TAURUS_CONTINENTAL_MUSCULAR", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 1.05, "ingesta_materia_seca_max_pct": 2.9, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Rapida", "umbral_termico_confort_c": 28.0},
    "simmental": {"biotipo_metabolico": "TAURUS_CONTINENTAL_MUSCULAR", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 1.04, "ingesta_materia_seca_max_pct": 2.9, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Rapida", "umbral_termico_confort_c": 27.5},
    "limousin": {"biotipo_metabolico": "TAURUS_CONTINENTAL_MUSCULAR", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 1.03, "ingesta_materia_seca_max_pct": 2.75, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Rapida", "umbral_termico_confort_c": 28.5},
    "suizo_europeo": {"biotipo_metabolico": "TAURUS_CONTINENTAL_MUSCULAR", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 1.06, "ingesta_materia_seca_max_pct": 2.95, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Rapida", "umbral_termico_confort_c": 26.0},
    "holstein": {"biotipo_metabolico": "TAURUS_LECHERO_INTENSIVO", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 1.20, "ingesta_materia_seca_max_pct": 3.2, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Muy Rapida", "umbral_termico_confort_c": 25.0},
    "jersey": {"biotipo_metabolico": "TAURUS_LECHERO_INTENSIVO", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 1.15, "ingesta_materia_seca_max_pct": 3.1, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Muy Rapida", "umbral_termico_confort_c": 27.0},

    # --- CRUZAS SINTÉTICAS
    "brangus": {"biotipo_metabolico": "SINTETICA_CARNE_TROPICAL", "proporcion_indicus": 0.375, "factor_mantenimiento_enm": 0.95, "ingesta_materia_seca_max_pct": 2.7, "indice_reciclaje_urea_saliva": 1.10, "tasa_paso_ruminal": "Media", "umbral_termico_confort_c": 32.0},
    "braford": {"biotipo_metabolico": "SINTETICA_CARNE_TROPICAL", "proporcion_indicus": 0.375, "factor_mantenimiento_enm": 0.94, "ingesta_materia_seca_max_pct": 2.65, "indice_reciclaje_urea_saliva": 1.10, "tasa_paso_ruminal": "Media", "umbral_termico_confort_c": 32.0},
    "charbray": {"biotipo_metabolico": "SINTETICA_CONTINENTAL_RUSTICA", "proporcion_indicus": 0.375, "factor_mantenimiento_enm": 1.00, "ingesta_materia_seca_max_pct": 2.8, "indice_reciclaje_urea_saliva": 1.08, "tasa_paso_ruminal": "Media Rapida", "umbral_termico_confort_c": 31.5},
    "simbrah": {"biotipo_metabolico": "SINTETICA_DOBLE_PROPOSITO", "proporcion_indicus": 0.375, "factor_mantenimiento_enm": 0.99, "ingesta_materia_seca_max_pct": 2.8, "indice_reciclaje_urea_saliva": 1.10, "tasa_paso_ruminal": "Media Rapida", "umbral_termico_confort_c": 32.0},
    "simangus": {"biotipo_metabolico": "CRUZA_EUROPEA_ACELERADA", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 1.02, "ingesta_materia_seca_max_pct": 2.85, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Rapida", "umbral_termico_confort_c": 27.5},
    "black_baldy": {"biotipo_metabolico": "CRUZA_BRITANICA_ACELERADA", "proporcion_indicus": 0.0, "factor_mantenimiento_enm": 0.99, "ingesta_materia_seca_max_pct": 2.8, "indice_reciclaje_urea_saliva": 1.00, "tasa_paso_ruminal": "Rapida", "umbral_termico_confort_c": 27.0},
    "nelangus": {"biotipo_metabolico": "SINTETICA_F1_TROPICAL", "proporcion_indicus": 0.5, "factor_mantenimiento_enm": 0.94, "ingesta_materia_seca_max_pct": 2.65, "indice_reciclaje_urea_saliva": 1.15, "tasa_paso_ruminal": "Media", "umbral_termico_confort_c": 33.5},
    "suizo_cebu": {"biotipo_metabolico": "SINTETICA_DOBLE_PROPOSITO", "proporcion_indicus": 0.5, "factor_mantenimiento_enm": 0.97, "ingesta_materia_seca_max_pct": 2.75, "indice_reciclaje_urea_saliva": 1.15, "tasa_paso_ruminal": "Media", "umbral_termico_confort_c": 33.0},
    "girolando": {"biotipo_metabolico": "SINTETICA_LECHE_TROPICAL", "proporcion_indicus": 0.5, "factor_mantenimiento_enm": 1.04, "ingesta_materia_seca_max_pct": 2.9, "indice_reciclaje_urea_saliva": 1.15, "tasa_paso_ruminal": "Media Rapida", "umbral_termico_confort_c": 31.0},
    "beefmaster": {"biotipo_metabolico": "SINTETICA_TRI_CRUZA", "proporcion_indicus": 0.5, "factor_mantenimiento_enm": 0.95, "ingesta_materia_seca_max_pct": 2.7, "indice_reciclaje_urea_saliva": 1.12, "tasa_paso_ruminal": "Media", "umbral_termico_confort_c": 33.0},
    "brahmousin": {"biotipo_metabolico": "SINTETICA_CONTINENTAL_RUSTICA", "proporcion_indicus": 0.375, "factor_mantenimiento_enm": 0.98, "ingesta_materia_seca_max_pct": 2.7, "indice_reciclaje_urea_saliva": 1.08, "tasa_paso_ruminal": "Media", "umbral_termico_confort_c": 32.0}
}

def obtener_perfil_metabolico(raza_input: str) -> Dict[str, Any]:
    texto = raza_input.lower().strip()
    texto_exacto = texto.replace(" ", "_")
    
    if texto_exacto in CODEX_METABOLICO:
        return CODEX_METABOLICO[texto_exacto]
        
    razas_encontradas = []
    for clave in CODEX_METABOLICO.keys():
        patron = r'\b' + clave.replace('_', r'[\s_]+') + r'\b'
        match = re.search(patron, texto)
        if match:
            razas_encontradas.append((match.start(), clave))
            
    if razas_encontradas:
        razas_encontradas.sort(key=lambda x: x[0])
        primera_raza = razas_encontradas[0][1]
        return CODEX_METABOLICO[primera_raza]
        
    return {
        "biotipo_metabolico": "GENERICO_DESCONOCIDO",
        "proporcion_indicus": 0.5,
        "factor_mantenimiento_enm": 1.00,
        "ingesta_materia_seca_max_pct": 2.7,
        "indice_reciclaje_urea_saliva": 1.05,
        "tasa_paso_ruminal": "Media",
        "umbral_termico_confort_c": 30.0
    }

def evaluar_riesgo_termico(raza: str, temperatura: float) -> Dict[str, Any]:
    perfil = obtener_perfil_metabolico(raza)
    limite = perfil["umbral_termico_confort_c"]
    
    riesgo = temperatura > limite
    exceso = round(temperatura - limite, 1)
    
    if not riesgo:
        mensaje = f"✅ CLIMA CONFORTABLE: Temperatura de {temperatura}°C dentro del rango de confort para su perfil."
    elif exceso <= 3.0:
        mensaje = f"⚠️ RIESGO MODERADO: La temperatura de {temperatura}°C está en el límite para esta genética ({limite}°C máx)."
    else:
        mensaje = f"❌ INCOMPATIBILIDAD GRAVE: Un animal {perfil['biotipo_metabolico']} a {temperatura}°C sufrirá estrés térmico severo."

    return {
        "raza_detectada": raza.title(),
        "tipo_genetico": perfil["biotipo_metabolico"],
        "limite_termico": limite,
        "temperatura_actual": temperatura,
        "riesgo_termico": riesgo,
        "mensaje": mensaje
    }