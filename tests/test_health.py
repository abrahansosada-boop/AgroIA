import pytest
from agroia.domain.health import calcular_protocolo_sanitario, calcular_meta_ganancia, evaluar_rendimiento_pesada

# Mocks alineados al nuevo esquema de farmacocinética (mg/kg / mg/ml)
DESP_ESTANDAR = {
    "dosis_base_mg_kg": 0.2, 
    "concentracion_mg_ml": 10.0, 
    "costo_estimado_ml": 5.0, 
    "tiempo_retiro_dias": 28,
    "via_administracion": "SC"
}

VACUNA_ESTANDAR = {
    "dosis_fija_ml": 2.0, 
    "costo_estimado_dosis": 35.0, 
    "tiempo_retiro_dias": 21,
    "via_administracion": "IM"
}

def test_protocolo_calcula_dosis_y_retiros_exactos():
    """Verifica que el software calcule miligramos reales sobre la concentración del frasco."""
    # Cálculo: (200kg * 0.2mg/kg) / 10mg/ml = 4.0ml
    resultado = calcular_protocolo_sanitario(200.0, DESP_ESTANDAR, VACUNA_ESTANDAR)
    
    assert resultado["dosis_desparasitante_ml"] == 4.0
    assert resultado["costo_total"] == 55.0 # (4ml * 5.0) + 35.0
    assert resultado["dias_retiro"] == 28
    assert resultado["apto_para_venta"] is False

@pytest.mark.parametrize("peso, desp, vac, retiro_esperado, apto_esperado", [
    (200.0, None, None, 0, True),
    (500.0, DESP_ESTANDAR, None, 28, False),
    (150.0, None, VACUNA_ESTANDAR, 21, False),
])
def test_protocolo_casos_limite(peso, desp, vac, retiro_esperado, apto_esperado):
    resultado = calcular_protocolo_sanitario(peso, desp, vac)
    assert resultado["dias_retiro"] == retiro_esperado
    assert resultado["apto_para_venta"] is apto_esperado

@pytest.mark.parametrize("proteina, esperado", [(14.0, 0.80), (16.0, 0.90), (12.0, 0.70)])
def test_calcular_meta_ganancia(proteina: float, esperado: float) -> None:
    assert calcular_meta_ganancia(proteina) == esperado

@pytest.mark.parametrize("peso_ant, peso_act, dias, meta, exp_gdp, exp_estado", [
    (180.0, 200.0, 10, 1.5, 2.0, "EXCELENTE"),
    (180.0, 193.0, 10, 1.5, 1.3, "ALERTA"),
    (180.0, 185.0, 10, 1.5, 0.5, "PELIGRO"),
])
def test_evaluar_rendimiento_pesada_valido(peso_ant, peso_act, dias, meta, exp_gdp, exp_estado):
    res = evaluar_rendimiento_pesada(peso_ant, peso_act, dias, meta)
    assert res["exito"] is True
    assert res["gdp_real"] == exp_gdp
    assert res["estado"] == exp_estado

def test_evaluar_rendimiento_pesada_errores():
    res_peso = evaluar_rendimiento_pesada(200.0, 190.0, 10, 1.5)
    assert res_peso["exito"] is False
    assert "catabolismo" in res_peso["error"]