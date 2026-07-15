import pytest
from agroia.lots import build_lot_profile

@pytest.mark.parametrize(
    "entrada, id_esperado, nombre_esperado, raza_esperada, genero_esperado",
    [
        ({"id": 42, "nombre_lote": "Corral Norte", "raza": "Brahman", "genero": "Macho"}, 42, "Corral Norte", "Brahman", "Macho"),
        ({"id": 15, "nombre_lote": "Engorda Fase 1", "raza": "Angus", "genero": "Hembra"}, 15, "Engorda Fase 1", "Angus", "Hembra"),
        ({}, None, None, None, None)
    ]
)
def test_build_lot_profile_parametrizado(entrada, id_esperado, nombre_esperado, raza_esperada, genero_esperado):
    perfil = build_lot_profile(entrada)
    
    assert perfil.get("id") == id_esperado
    assert perfil.get("nombre_lote") == nombre_esperado
    assert perfil.get("raza") == raza_esperada
    assert perfil.get("genero") == genero_esperado
