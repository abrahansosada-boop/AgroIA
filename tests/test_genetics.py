import pytest
from agroia.domain.genetics import evaluar_riesgo_termico

@pytest.mark.parametrize("raza, temperatura, riesgo_esperado, tipo_esperado", [
    ("angus", 36.0, True, "Taurus"),              
    ("brahman", 38.0, False, "Indicus"),          
    ("brangus (brahman x angus)", 31.0, False, "Sintética"), 
    ("holstein", 36.0, True, "Taurus"),                     
    ("Vaca Marciana", 25.0, False, "Desconocida"),
])
def test_evaluacion_riesgo_termico(raza, temperatura, riesgo_esperado, tipo_esperado):
    resultado = evaluar_riesgo_termico(raza, temperatura)
    assert resultado["riesgo_termico"] is riesgo_esperado
    assert resultado["tipo_genetico"] == tipo_esperado