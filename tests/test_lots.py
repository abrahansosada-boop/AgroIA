from agroia.lots import build_lot_profile, get_active_lot_id, get_active_lot_name


def test_build_lot_profile_keeps_operational_id() -> None:
    profile = build_lot_profile(
        {
            "id": 42,
            "nombre_lote": "Corral norte",
            "raza": "brahman",
            "genero": "Macho",
            "proposito": "Carne",
            "edad": 8,
            "peso_promedio": 240,
            "clima_local": 32,
            "costo_salud": 12.5,
        }
    )

    assert profile["lote_id"] == 42
    assert profile["nombre"] == "Corral norte"
    assert profile["peso"] == 240.0


def test_get_active_lot_helpers_return_none_without_profile() -> None:
    assert get_active_lot_id({}) is None
    assert get_active_lot_name({}) is None


def test_get_active_lot_helpers_read_session_profile() -> None:
    session_state = {"perfil": {"lote_id": 42, "nombre": "Corral norte"}}

    assert get_active_lot_id(session_state) == 42
    assert get_active_lot_name(session_state) == "Corral norte"
