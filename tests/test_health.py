import pytest
from agroia.domain.health import calcular_protocolo_sanitario

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