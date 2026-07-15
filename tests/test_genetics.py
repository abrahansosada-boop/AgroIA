import pytest
from agroia.domain.genetics import evaluar_riesgo_termico, obtener_perfil_metabolico

@pytest.mark.parametrize(
    ("raza", "temperatura", "riesgo_esperado", "biotipo_esperado", "limite_esperado"),
    [
        ("angus", 27.0, False, "TAURUS_METABOLISMO_ACELERADO", 27.0),
        ("angus", 28.5, True, "TAURUS_METABOLISMO_ACELERADO", 27.0),
        ("holstein", 35.0, True, "TAURUS_LECHERO_INTENSIVO", 25.0),
        ("brahman", 35.0, False, "INDICUS_FIBRAL_RUSTICO", 35.0),
        ("gyr", 36.0, True, "INDICUS_LECHE_TROPICAL", 34.0),
        ("brangus", 31.0, False, "SINTETICA_CARNE_TROPICAL", 32.0),
        ("simangus", 28.0, True, "CRUZA_EUROPEA_ACELERADA", 27.5),
        (" Vaca Marciana ", 25.0, False, "GENERICO_DESCONOCIDO", 30.0),
        ("toro_desconocido", 35.0, True, "GENERICO_DESCONOCIDO", 30.0),
    ]
)
def test_evaluacion_riesgo_termico_parametrizado(
    raza: str, 
    temperatura: float, 
    riesgo_esperado: bool, 
    biotipo_esperado: str, 
    limite_esperado: float
) -> None:
    resultado = evaluar_riesgo_termico(raza, temperatura)
    
    assert resultado["riesgo_termico"] is riesgo_esperado
    assert resultado["tipo_genetico"] == biotipo_esperado
    assert resultado["limite_termico"] == limite_esperado
    assert isinstance(resultado["mensaje"], str)
    assert resultado["raza_detectada"] == raza.title()

@pytest.mark.parametrize(
    ("raza_sucia", "biotipo_esperado", "indicus_esperado"),
    [
        ("Ganado Angus Negro", "TAURUS_METABOLISMO_ACELERADO", 0.0),
        ("Novillos Brahman de Registro", "INDICUS_FIBRAL_RUSTICO", 1.0),
        ("Cruza Brangus/Charolais", "SINTETICA_CARNE_TROPICAL", 0.375),
    ]
)
def test_inferencia_genetica_textos_compuestos(
    raza_sucia: str, 
    biotipo_esperado: str, 
    indicus_esperado: float
) -> None:
    perfil = obtener_perfil_metabolico(raza_sucia)
    
    assert perfil["biotipo_metabolico"] == biotipo_esperado
    assert perfil["proporcion_indicus"] == indicus_esperado