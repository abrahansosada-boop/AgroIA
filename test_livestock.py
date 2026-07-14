import pytest

from agroia.domain.livestock import (
    CalculoZootecnicoError,
    calcular_dosis_sanitaria,
    calcular_mezcla,
    optimizar_dieta,
    validar_inventario_para_receta,
)

BASE_DATOS = {
    "maiz": {
        "proteina_bruta_pct": 8.0,
        "energia_metabolizable_mcal": 3.3,
        "fdn_pct": 9.0,
        "indice_efectividad_fdn": 0.15,
        "costo_kg": 4.0,
        "stock_kg": 100.0,
        "max_pct": 80.0,
    },
    "soya": {
        "proteina_bruta_pct": 44.0,
        "energia_metabolizable_mcal": 2.9,
        "fdn_pct": 15.0,
        "indice_efectividad_fdn": 0.20,
        "costo_kg": 11.0,
        "stock_kg": 30.0,
        "max_pct": 30.0,
    },
    "rastrojo": {
        "proteina_bruta_pct": 4.0,
        "energia_metabolizable_mcal": 1.8,
        "fdn_pct": 78.0,
        "indice_efectividad_fdn": 0.90,
        "costo_kg": 1.5,
        "stock_kg": 100.0,
        "max_pct": 40.0,
    },
}

def test_calcular_mezcla_y_costo_por_kg() -> None:
    resultado = calcular_mezcla(BASE_DATOS, {"maiz": 80, "soya": 20})

    assert resultado["total_kilos"] == 100
    assert resultado["proteina"] == pytest.approx(15.2)  # (80*8 + 20*44) / 100
    assert resultado["energia"] == pytest.approx(3.22)   # (80*3.3 + 20*2.9) / 100
    assert resultado["costo_total"] == pytest.approx(540.0)
    assert resultado["costo_kg"] == pytest.approx(5.4)


def test_calcular_mezcla_rechaza_kilos_cero() -> None:
    with pytest.raises(CalculoZootecnicoError):
        calcular_mezcla(BASE_DATOS, {"maiz": 0})


def test_calcular_dosis_sanitaria() -> None:
    # Usando el estándar de mg/kg en el mock
    desparasitante = {
        "dosis_base_mg_kg": 0.2,
        "concentracion_mg_ml": 10.0,
        "costo_estimado_ml": 2.5,
        "tiempo_retiro_dias": 30,
    }
    vacuna = {"dosis_fija_ml": 5.0, "costo_estimado_dosis": 20.0, "tiempo_retiro_dias": 7}

    resultado = calcular_dosis_sanitaria(250, desparasitante, vacuna)

    assert resultado["dosis_desparasitante_ml"] == pytest.approx(5.0)
    assert resultado["costo_desparasitante"] == pytest.approx(12.5)
    assert resultado["dosis_vacuna_ml"] == pytest.approx(5.0)
    assert resultado["costo_total"] == pytest.approx(32.5)
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
            "proteina_bruta_pct": 50,
            "energia_metabolizable_mcal": 3.5,
            "fdn_pct": 3,
            "indice_efectividad_fdn": 0.1,
            "costo_kg": 1,
            "stock_kg": 0,
        },
        "maiz": BASE_DATOS["maiz"],
        "soya": BASE_DATOS["soya"],
        # Inyectamos fibra física para que el Escudo QFB permita formular la dieta
        "rastrojo": BASE_DATOS["rastrojo"], 
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
    assert "Inviable" in resultado.estado or "No existe una mezcla viable" in resultado.mensaje