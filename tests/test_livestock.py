import pytest

from motores.calculos_zootecnicos import (
    CalculoZootecnicoError,
    calcular_dosis_sanitaria,
    calcular_mezcla,
    optimizar_dieta,
    validar_inventario_para_receta,
)


BASE_DATOS = {
    "maiz": {
        "proteina_pct": 8.0,
        "energia_mcal": 3.3,
        "fibra_pct": 2.0,
        "costo_kg": 4.0,
        "stock_kg": 100.0,
        "max_pct": 80.0,
    },
    "soya": {
        "proteina_pct": 44.0,
        "energia_mcal": 2.9,
        "fibra_pct": 7.0,
        "costo_kg": 11.0,
        "stock_kg": 30.0,
        "max_pct": 30.0,
    },
    "rastrojo": {
        "proteina_pct": 4.0,
        "energia_mcal": 1.8,
        "fibra_pct": 35.0,
        "costo_kg": 1.5,
        "stock_kg": 100.0,
        "max_pct": 40.0,
    },
}


def test_calcular_mezcla_y_costo_por_kg() -> None:
    resultado = calcular_mezcla(BASE_DATOS, {"maiz": 80, "soya": 20})

    assert resultado["total_kilos"] == 100
    assert resultado["proteina"] == pytest.approx(15.2)
    assert resultado["energia"] == pytest.approx(3.22)
    assert resultado["costo_total"] == pytest.approx(540.0)
    assert resultado["costo_kg"] == pytest.approx(5.4)


def test_calcular_mezcla_rechaza_kilos_cero() -> None:
    with pytest.raises(CalculoZootecnicoError):
        calcular_mezcla(BASE_DATOS, {"maiz": 0})


def test_calcular_dosis_sanitaria() -> None:
    desparasitante = {
        "dosis_ml_por_kg": 0.01,
        "costo_por_ml": 2.5,
        "tiempo_retiro_dias": 30,
    }
    vacuna = {"dosis_ml_fija": 5.0, "costo_por_dosis": 20.0, "tiempo_retiro_dias": 7}

    resultado = calcular_dosis_sanitaria(200, desparasitante, vacuna)

    assert resultado["dosis_desparasitante_ml"] == pytest.approx(2.0)
    assert resultado["costo_desparasitante"] == pytest.approx(5.0)
    assert resultado["dosis_vacuna_ml"] == pytest.approx(5.0)
    assert resultado["costo_total"] == pytest.approx(25.0)
    assert resultado["retiro_dias"] == pytest.approx(30.0)


def test_validar_inventario_detecta_stock_cero_e_insuficiente() -> None:
    inventario = {
        "maiz": {"stock_kg": 0},
        "soya": {"stock_kg": 10},
    }

    errores = validar_inventario_para_receta(inventario, {"maiz": 1, "soya": 20})

    assert "maiz: stock cero" in errores
    assert "soya: requiere 20.00 kg y solo hay 10.00 kg" in errores


def test_optimizador_ignora_ingredientes_sin_stock() -> None:
    base = {
        "barato_sin_stock": {
            "proteina_pct": 50,
            "energia_mcal": 3.5,
            "fibra_pct": 3,
            "costo_kg": 1,
            "stock_kg": 0,
        },
        "maiz": BASE_DATOS["maiz"],
        "soya": BASE_DATOS["soya"],
    }

    resultado = optimizar_dieta(base, req_proteina=12, req_energia=2.8)

    assert resultado.estado == "Optimal"
    assert "barato_sin_stock" not in resultado.ingredientes


def test_optimizador_reporta_sin_mezcla_viable() -> None:
    base = {
        "rastrojo": {
            **BASE_DATOS["rastrojo"],
            "stock_kg": 100,
            "max_pct": 100,
        }
    }

    resultado = optimizar_dieta(base, req_proteina=20, req_energia=3.0)

    assert resultado.estado != "Optimal"
    assert resultado.ingredientes == {}
    assert "No existe una mezcla viable" in resultado.mensaje
