import pytest
from agroia.domain.health import calcular_protocolo_sanitario
from agroia.domain.health import calcular_meta_ganancia, evaluar_rendimiento_pesada, calcular_perdida_mortandad

# Datos simulados globales (Como el VALID_ENVIRONMENT)
DESP_ESTANDAR = {"dosis_ml_por_kg": 0.02, "costo_por_ml": 5.0, "tiempo_retiro_dias": 28}
VACUNA_ESTANDAR = {"dosis_ml_fija": 2.0, "costo_por_dosis": 35.0, "tiempo_retiro_dias": 21}

def test_protocolo_calcula_costos_y_retiros_correctamente():
    """Verifica la matemática pura del botiquín."""
    resultado = calcular_protocolo_sanitario(200.0, DESP_ESTANDAR, VACUNA_ESTANDAR)
    
    assert resultado["dosis_desparasitante_ml"] == 4.0
    assert resultado["costo_total"] == 55.0
    assert resultado["dias_retiro"] == 28
    assert resultado["apto_para_venta"] is False

@pytest.mark.parametrize("peso, desp, vac, retiro_esperado, apto_esperado", [
    (200.0, None, None, 0, True),                     
    (500.0, DESP_ESTANDAR, None, 28, False),          
    (150.0, None, VACUNA_ESTANDAR, 21, False),        
    (0.0, None, None, 0, True),                       
])
def test_protocolo_casos_limite(peso, desp, vac, retiro_esperado, apto_esperado):
    """Evalúa omisiones de usuario y combinaciones incompletas usando parametrización."""
    resultado = calcular_protocolo_sanitario(peso, desp, vac)
    
    assert resultado["dias_retiro"] == retiro_esperado
    assert resultado["apto_para_venta"] is apto_esperado

import pytest
from agroia.domain.health import calcular_meta_ganancia, evaluar_rendimiento_pesada

@pytest.mark.parametrize(
    "proteina, esperado",
    [
        (14.0, 0.80),
        (16.0, 0.90),
        (12.0, 0.70)
    ]
)
def test_calcular_meta_ganancia(proteina: float, esperado: float) -> None:
    assert calcular_meta_ganancia(proteina) == esperado

@pytest.mark.parametrize(
    "peso_ant, peso_act, dias, meta, exp_gdp, exp_estado",
    [
        (180.0, 200.0, 10, 1.5, 2.0, "EXCELENTE"),   # GDP de 2.0 supera la meta de 1.5
        (180.0, 193.0, 10, 1.5, 1.3, "ALERTA"),      # GDP de 1.3 está arriba del 80% (1.2) pero no llega a 1.5
        (180.0, 185.0, 10, 1.5, 0.5, "PELIGRO"),     # GDP de 0.5 está en el hoyo
    ]
)

def test_evaluar_rendimiento_pesada_valido(peso_ant: float, peso_act: float, dias: int, meta: float, exp_gdp: float, exp_estado: str) -> None:
    res = evaluar_rendimiento_pesada(peso_ant, peso_act, dias, meta)
    assert res["exito"] is True
    assert res["gdp_real"] == exp_gdp
    assert res["estado"] == exp_estado

def test_evaluar_rendimiento_pesada_errores() -> None:
    # Error: Animal bajó de peso
    res_peso = evaluar_rendimiento_pesada(200.0, 190.0, 10, 1.5)
    assert res_peso["exito"] is False
    assert "menor o igual" in res_peso["error"]

    # Error: Días en cero o negativo
    res_dias = evaluar_rendimiento_pesada(180.0, 200.0, 0, 1.5)
    assert res_dias["exito"] is False
    assert "mayores a cero" in res_dias["error"]

@pytest.mark.parametrize(
    "bajas, vacunado, costo_unitario, exp_perdida",
    [
        (2, True, 50.0, 100.0),   # 2 bajas vacunadas = 100 de pérdida
        (1, False, 50.0, 0.0),    # 1 baja sin vacunar = 0 pérdida
        (5, True, 100.0, 500.0),  # 5 bajas con vacuna cara = 500 de pérdida
    ]
)
def test_calcular_perdida_mortandad_valido(bajas: int, vacunado: bool, costo_unitario: float, exp_perdida: float) -> None:
    res = calcular_perdida_mortandad(bajas, vacunado, costo_unitario)
    assert res["exito"] is True
    assert res["perdida_medica"] == exp_perdida

def test_calcular_perdida_mortandad_errores() -> None:
    res = calcular_perdida_mortandad(0, True, 50.0)  # Cero bajas
    assert res["exito"] is False
    assert "mayor a cero" in res["error"]