import pytest
from agroia.repositories.inventory import (
    evaluar_alerta_dias, 
    evaluar_alerta_kilos, 
    procesar_movimiento_bodega, 
    convertir_precio_chicago
)

@pytest.mark.parametrize(
    "stock, consumo, limite, exp_dias, exp_estado",
    [
        (1000.0, 100.0, 3, 10.0, "🟢 ÓPTIMO (10.0 días)"),
        (400.0, 100.0, 3, 4.0, "🟡 PRECAUCIÓN (4.0 días)"),
        (200.0, 100.0, 3, 2.0, "🔴 CRÍTICO (2.0 días)"),
        (100.0, 0.0, 3, 0.0, "🔴 CRÍTICO (0.0 días)") # Consumo cero
    ]
)
def test_evaluar_alerta_dias(stock: float, consumo: float, limite: int, exp_dias: float, exp_estado: str) -> None:
    res = evaluar_alerta_dias(stock, consumo, limite)
    assert res["dias"] == exp_dias
    assert res["estado"] == exp_estado

@pytest.mark.parametrize(
    "stock, limite, exp_estado",
    [
        (1500.0, 500.0, "🟢 ÓPTIMO"),
        (800.0, 500.0, "🟡 PRECAUCIÓN"),
        (300.0, 500.0, "🔴 CRÍTICO")
    ]
)
def test_evaluar_alerta_kilos(stock: float, limite: float, exp_estado: str) -> None:
    assert evaluar_alerta_kilos(stock, limite) == exp_estado

def test_procesar_movimiento_ingreso() -> None:
    res = procesar_movimiento_bodega(100.0, 10.0, 50.0, "Ingreso", 12.0)
    assert res["exito"] is True
    assert res["nuevo_stock"] == 150.0
    assert res["precio_final"] == 12.0

def test_procesar_movimiento_merma() -> None:
    res = procesar_movimiento_bodega(100.0, 10.0, 20.0, "Merma")
    assert res["exito"] is True
    assert res["nuevo_stock"] == 80.0
    assert res["perdida_dinero"] == 200.0

def test_convertir_precio_chicago() -> None:
    # Ej: Dolar a 20 MXN, Maiz a 450 centavos/bushel
    # Bushel = $4.50 USD. Kilo = 4.50 / 25.401 = $0.177 USD. En MXN = 0.177 * 20 = 3.54
    res = convertir_precio_chicago(20.0, 450.0)
    assert res == 3.54