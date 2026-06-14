from unittest.mock import MagicMock

from agroia.data import registrar_bitacora


def test_registrar_bitacora_uses_supplied_client() -> None:
    db = MagicMock()

    result = registrar_bitacora(
        db,
        "Control de Peso",
        "Pesada registrada",
        gasto_total=125,
        kilos_procesados=42,
    )

    db.table.assert_called_once_with("bitacora")
    db.table.return_value.insert.assert_called_once_with(
        {
            "accion": "Control de Peso",
            "detalle": "Pesada registrada",
            "gasto_total": 125.0,
            "kilos_procesados": 42.0,
        }
    )
    db.table.return_value.insert.return_value.execute.assert_called_once_with()
    assert result is True
