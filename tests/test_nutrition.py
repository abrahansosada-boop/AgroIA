import pytest
import pandas as pd
from agroia.domain.nutrition import calcular_correccion_pearson, auditar_mezcla_manual, optimizar_dieta_pulp
from agroia.domain.nutrition import (calcular_rendimiento_nopal, 
    calcular_rotacion_prv, 
    calcular_biomasa_azolla, 
    calcular_enriquecimiento_esquilmos, 
    calcular_silo_tamo, 
    calcular_proyeccion_sspi, 
    calcular_efecto_boma, 
    calcular_roi_cercos_virtuales,
)
MOCK_BODEGA_PERFECTA = {
    "maiz_molido": {"proteina_pct": 0.08, "energia_mcal": 3.3, "fibra_pct": 0.02, "costo_kg": 5.5, "stock_kg": 5000.0, "max_pct": 70.0},
    "pasta_soya": {"proteina_pct": 0.45, "energia_mcal": 3.0, "fibra_pct": 0.06, "costo_kg": 11.0, "stock_kg": 3000.0, "max_pct": 40.0},
    "tamo_trigo": {"proteina_pct": 0.03, "energia_mcal": 1.5, "fibra_pct": 0.40, "costo_kg": 2.5, "stock_kg": 2000.0, "max_pct": 20.0}
}

MOCK_BODEGA_VACIA = {}

MOCK_BODEGA_SIN_STOCK = {
    "maiz_molido": {"proteina_pct": 0.08, "energia_mcal": 3.3, "costo_kg": 5.5, "stock_kg": 0.0},
    "pasta_soya": {"proteina_pct": 0.45, "energia_mcal": 3.0, "costo_kg": 11.0, "stock_kg": 0.0}
}


# PRUEBAS PARA EL CUADRADO DE PEARSON
@pytest.mark.parametrize("prot_act, kilos, prot_obj, prot_ref, exito_esperado, kilos_esperados", [
    (11.0, 1000.0, 14.0, 45.0, True, 96.77),  
    (10.0, 500.0, 15.0, 40.0, True, 100.0),    
    (12.0, 1000.0, 10.0, 45.0, False, None),  
    (11.0, 1000.0, 48.0, 45.0, False, None),   
])
def test_cuadrado_pearson_parametrizado(prot_act, kilos, prot_obj, prot_ref, exito_esperado, kilos_esperados):
    """Evalúa escenarios válidos e inválidos del corrector de Pearson."""
    resultado = calcular_correccion_pearson(prot_act, kilos, prot_obj, prot_ref)
    
    assert resultado["exito"] is exito_esperado
    if exito_esperado:
        assert round(resultado["kilos_a_anadir"], 2) == kilos_esperados
    else:
        assert "error" in resultado


# PRUEBAS PARA LA AUDITORÍA MANUAL
def test_auditar_mezcla_manual_exitosa():
    mezcla = [
        {"kilos": 60.0, "datos": {"proteina_pct": 0.08, "energia_mcal": 3.0, "fibra_pct": 0.02, "costo_kg": 5.0}},
        {"kilos": 40.0, "datos": {"proteina_pct": 0.40, "energia_mcal": 2.5, "fibra_pct": 0.05, "costo_kg": 10.0}}
    ]
    resultado = auditar_mezcla_manual(mezcla)
    
    assert resultado["exito"] is True
    assert resultado["total_kilos"] == 100.0
    assert round(resultado["proteina"], 3) == 0.208  
    assert resultado["costo_total"] == 700.0

def test_auditar_mezcla_manual_vacia():
    """Valida que el sistema rechace mermas o mezclas con cero kilos."""
    resultado = auditar_mezcla_manual([])
    assert resultado["exito"] is False
    assert "Agregue kilos" in resultado["error"]


# PRUEBAS PARA EL MOTOR IA (PuLP)
def test_optimizar_dieta_ia_exitosa():
    """Verifica que el optimizador lineal resuelva una dieta viable económicamente."""
    # Pedimos 14% de proteína (0.14) y 2.4 Mcal de energía
    resultado = optimizar_dieta_pulp(MOCK_BODEGA_PERFECTA, req_proteina=0.14, req_energia=2.4)
    
    assert resultado["exito"] is True
    assert resultado["costo_kg"] > 0
    assert isinstance(resultado["df"], pd.DataFrame)
    assert "maiz_molido" in resultado["detalles_ia"]["kilos"]

@pytest.mark.parametrize("bodega, req_prot, req_ener, error_contenido", [
    (MOCK_BODEGA_VACIA, 0.14, 2.4, "vacía o sin stock"),
    (MOCK_BODEGA_SIN_STOCK, 0.14, 2.4, "vacía o sin stock"),
    (MOCK_BODEGA_PERFECTA, 0.80, 4.5, "No hay suficientes insumos"), # Requerimiento imposible (80% prot)
])
def test_optimizar_dieta_ia_errores_y_limites(bodega, req_prot, req_ener, error_contenido):
    """Prueba la resistencia del motor ante bodegas desprovistas o metas imposibles."""
    resultado = optimizar_dieta_pulp(bodega, req_prot, req_ener)
    
    assert resultado["exito"] is False
    assert error_contenido in resultado["error"]

# TESTS PILAR 1: RESILIENCIA

def test_calcular_rendimiento_nopal_valido() -> None:
    rendimiento = calcular_rendimiento_nopal(densidad_ha=10000, peso_penca=1.0, pencas_por_planta=4)
    assert rendimiento == 40.0

@pytest.mark.parametrize(
    "densidad, peso, pencas, esperado", 
    [
        (0, 1.5, 5, 0.0),          
        (10000, 0.0, 5, 0.0),      
        (20000, 1.5, 10, 300.0),   
    ]
)
def test_calcular_rendimiento_nopal_casos_borde(densidad: int, peso: float, pencas: int, esperado: float) -> None:
    assert calcular_rendimiento_nopal(densidad, peso, pencas) == esperado

@pytest.mark.parametrize(
    "densidad, peso, pencas, esperado", 
    [
        (10000, 1.2, 4, 48.0),     # Caso normal: 10k plantas, 1.2kg, 4 pencas = 48 Ton
        (0, 1.5, 5, 0.0),          # Error usuario: Cero densidad
        (10000, 0.0, 5, 0.0),      # Error usuario: Cero peso
        (20000, 1.5, 10, 300.0),   # Caso extremo de alta densidad
    ]
)
def test_calcular_rendimiento_nopal_casos(densidad: int, peso: float, pencas: int, esperado: float) -> None:
    assert calcular_rendimiento_nopal(densidad, peso, pencas) == esperado


@pytest.mark.parametrize(
    "espejos, m2, cosecha, dias, esp_ciclo, esp_anual",
    [
        (2, 10.0, 1.5, 15, 30.0, 0.73),  # Caso normal: 30kg ciclo, 0.73 Ton anual
        (2, 10.0, 1.5, 0, 0.0, 0.0),     # Error división por cero: 0 días
        (0, 10.0, 1.5, 15, 0.0, 0.0),    # Sin espejos de agua
    ]
)
def test_calcular_biomasa_azolla_casos(espejos: int, m2: float, cosecha: float, dias: int, esp_ciclo: float, esp_anual: float) -> None:
    res = calcular_biomasa_azolla(espejos, m2, cosecha, dias)
    assert res["ciclo_kg"] == esp_ciclo
    assert round(res["anual_ton"], 2) == esp_anual


@pytest.mark.parametrize(
    "tons, precio, tratamiento, esp_costo_ton, esp_pc, esp_costo_tot",
    [
        (10.0, 1000.0, "Urea y Melaza", 1450.0, 4.0, 14500.0),                     # Tratamiento Urea
        (10.0, 1000.0, "Inoculación de Hongos (Pleurotus)", 1800.0, 8.0, 18000.0), # Tratamiento Hongos
        (0.0, 1000.0, "Amonificación", 0.0, 6.0, 0.0),                             # Cero toneladas
    ]
)
def test_calcular_enriquecimiento_esquilmos_casos(tons: float, precio: float, tratamiento: str, esp_costo_ton: float, esp_pc: float, esp_costo_tot: float) -> None:
    res = calcular_enriquecimiento_esquilmos(tons, precio, tratamiento)
    assert res["costo_final_ton"] == esp_costo_ton
    assert res["incremento_pc"] == esp_pc
    assert res["costo_total"] == esp_costo_tot


@pytest.mark.parametrize(
    "tons_tamo, precio_tamo, lts_melaza, precio_melaza, lts_agua, esp_agua, esp_peso, esp_costo",
    [
        (1.0, 800.0, 20.0, 8.0, 1250.0, 1250.0, 2.27, 960.0),   # Caso base funcional
        (5.0, 800.0, 20.0, 8.0, 1250.0, 6250.0, 11.35, 4800.0), # Lote de 5 toneladas
        (0.0, 800.0, 20.0, 8.0, 1250.0, 0.0, 0.0, 0.0),         # Límite: 0 toneladas
    ]
)
def test_calcular_silo_tamo_casos(tons_tamo: float, precio_tamo: float, lts_melaza: float, precio_melaza: float, lts_agua: float, esp_agua: float, esp_peso: float, esp_costo: float) -> None:
    res = calcular_silo_tamo(tons_tamo, precio_tamo, lts_melaza, precio_melaza, lts_agua)
    assert res["agua_requerida_lts"] == esp_agua
    assert round(res["peso_final_ton"], 2) == esp_peso
    assert res["costo_total"] == esp_costo

# TESTS PILAR 2: SUELO Y MICROBIOLOGÍA

@pytest.mark.parametrize(
    "hectareas, carga_actual, multiplicador, valor_vaca, esp_nuevas, esp_incremento",
    [
        (10.0, 1.0, 3.0, 25000.0, 30.0, 20.0),  # Caso normal (Éxito)
        (0.0, 1.0, 3.0, 25000.0, 0.0, 0.0),     # Cero hectáreas (Límite)
        (10.0, 1.0, 1.0, 25000.0, 10.0, 0.0),   # Multiplicador 1x (Sin impacto real)
    ]
)
def test_calcular_proyeccion_sspi_casos(hectareas: float, carga_actual: float, multiplicador: float, valor_vaca: float, esp_nuevas: float, esp_incremento: float) -> None:
    res = calcular_proyeccion_sspi(hectareas, carga_actual, multiplicador, valor_vaca)
    assert res["vacas_nuevas_totales"] == esp_nuevas
    assert res["incremento_vacas"] == esp_incremento


@pytest.mark.parametrize(
    "cabezas, peso, costo_urea, esp_area, esp_ahorro",
    [
        (100, 400.0, 15.0, 240.0, 260.4),  # Caso normal
        (0, 400.0, 15.0, 0.0, 0.0),        # Corral vacío (Límite)
        (100, 0.0, 15.0, 0.0, 0.0),        # Peso cero (Error de usuario)
    ]
)
def test_calcular_efecto_boma_casos(cabezas: int, peso: float, costo_urea: float, esp_area: float, esp_ahorro: float) -> None:
    res = calcular_efecto_boma(cabezas, peso, costo_urea)
    assert res["area_m2"] == esp_area
    assert round(res["ahorro_diario"], 1) == esp_ahorro

# --- TESTS PILAR 3: ESCALABILIDAD Y PROCESOS

@pytest.mark.parametrize(
    "km_evitados, costo_km, cabezas, costo_collar, esp_ahorro",
    [
        (10.0, 35000.0, 50, 3000.0, 200000.0),  # Escenario rentable
        (1.0, 35000.0, 50, 3000.0, -115000.0),  # Escenario de PÉRDIDA (Hardware muy caro para tan poco cerco)
        (0.0, 0.0, 0, 0.0, 0.0),                # Sin datos
    ]
)
def test_calcular_roi_cercos_casos(km_evitados: float, costo_km: float, cabezas: int, costo_collar: float, esp_ahorro: float) -> None:
    res = calcular_roi_cercos_virtuales(km_evitados, costo_km, cabezas, costo_collar)
    assert res["ahorro_infraestructura"] == esp_ahorro

@pytest.mark.parametrize(
    "ha, aforo, cabezas, peso, aprovechamiento, esp_forraje, esp_consumo, esp_dias",
    [
        (1.0, 2.0, 100, 400.0, 50.0, 10.0, 4000.0, 2.5),  # Escenario ideal: 2.5 días
        (1.0, 2.0, 0, 400.0, 50.0, 10.0, 0.0, 0.0),       # Límite: Cero cabezas 
        (2.0, 1.5, 50, 350.0, 40.0, 12.0, 1750.0, 6.86),  # Escenario de advertencia: > 3 días
    ]
)
def test_calcular_rotacion_prv_casos(ha: float, aforo: float, cabezas: int, peso: float, aprovechamiento: float, esp_forraje: float, esp_consumo: float, esp_dias: float) -> None:
    res = calcular_rotacion_prv(ha, aforo, cabezas, peso, aprovechamiento)
    assert res["forraje_util_ton"] == esp_forraje
    assert res["consumo_diario_kg"] == esp_consumo
    assert round(res["dias_ocupacion"], 2) == esp_dias