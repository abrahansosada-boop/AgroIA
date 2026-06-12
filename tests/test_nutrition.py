import pytest
import pandas as pd
from agroia.domain.nutrition import calcular_correccion_pearson, auditar_mezcla_manual, optimizar_dieta_pulp

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