import pytest
from agroia.domain.nutrition import calcular_correccion_pearson, auditar_mezcla_manual

def test_pearson_exitoso():
    # Simulamos una tolva con 1000kg al 11%, queriendo llegar al 14% con pasta de soya al 45%
    resultado = calcular_correccion_pearson(
        prot_actual=11.0, 
        kilos_tolva=1000.0, 
        prot_objetivo=14.0, 
        prot_refuerzo=45.0
    )
    assert resultado["exito"] is True
    # Debería sugerir aprox 96.77 kilos
    assert round(resultado["kilos_a_anadir"], 2) == 96.77

def test_pearson_mision_imposible():
    # Querer llegar a 14% de proteína usando un refuerzo que solo tiene 10%
    resultado = calcular_correccion_pearson(11.0, 1000.0, 14.0, 10.0)
    assert resultado["exito"] is False
    assert "ENTRE la actual y la del refuerzo" in resultado["error"]

def test_auditar_mezcla_manual():
    # Simulamos que el usuario metió 50kg de maiz y 50kg de soya
    mezcla_simulada = [
        {"nombre": "maiz", "kilos": 50, "datos": {"proteina_pct": 8.0, "energia_mcal": 3.0, "fibra_pct": 2.0, "costo_kg": 5.0}},
        {"nombre": "soya", "kilos": 50, "datos": {"proteina_pct": 45.0, "energia_mcal": 2.5, "fibra_pct": 6.0, "costo_kg": 10.0}}
    ]
    
    resultado = auditar_mezcla_manual(mezcla_simulada)
    
    assert resultado["exito"] is True
    assert resultado["total_kilos"] == 100.0
    assert resultado["proteina"] == 26.5  # Promedio de 8 y 45
    assert resultado["costo_total"] == 750.0 # (50*5) + (50*10)