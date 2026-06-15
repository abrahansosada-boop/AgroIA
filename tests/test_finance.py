import pytest
import pandas as pd
from datetime import datetime
from agroia.domain.finance import calcular_kpis_auditoria, procesar_datos_graficas

@pytest.mark.parametrize(
    "datos, exp_gasto, exp_movimientos",
    [
        # Caso 1: Escenario ideal con gastos válidos
        ({"accion": ["Compra", "Merma"], "gasto_total": [1000.0, 500.0]}, 1500.0, 2),
        
        # Caso 2: Faltan datos financieros (columna gasto_total no existe)
        ({"accion": ["Registro", "Visita"]}, 0.0, 0),
        
        # Caso 3: Base de datos completamente vacía
        ({}, 0.0, 0),
        
        # Caso 4: Movimientos que no generaron costo (0.0)
        ({"accion": ["Ajuste", "Movimiento"], "gasto_total": [0.0, 0.0]}, 0.0, 2),
    ]
)
def test_calcular_kpis_auditoria_casos(datos: dict, exp_gasto: float, exp_movimientos: int) -> None:
    df = pd.DataFrame(datos)
    res = calcular_kpis_auditoria(df)
    
    assert res["gasto_total"] == exp_gasto
    assert res["total_movimientos"] == exp_movimientos


@pytest.mark.parametrize(
    "datos, exp_gastos_len, exp_tiempo_len, exp_tabla_len",
    [
        # Caso 1: Normal (1 movimiento con gasto > 0, 1 movimiento con gasto 0)
        ({
            "fecha": [datetime(2026, 6, 15, 10, 0), datetime(2026, 6, 15, 11, 0)],
            "accion": ["Compra", "Ajuste"],
            "detalle": ["Compramos melaza", "Ajuste de kilos"],
            "gasto_total": [1000.0, 0.0]
        }, 1, 1, 2), # df_gastos debe tener 1, df_tiempo 1 (agrupado), df_tabla 2
        
        # Caso 2: Base de datos vacía
        ({}, 0, 0, 0),
        
        # Caso 3: Todo fue gratis (sin gastos mayores a cero)
        ({
            "fecha": [datetime(2026, 6, 15, 10, 0)],
            "accion": ["Ajuste"],
            "detalle": ["Ajuste manual"],
            "gasto_total": [0.0]
        }, 0, 0, 1) # df_gastos debe ser 0, df_tabla sigue teniendo 1 registro
    ]
)
def test_procesar_datos_graficas_casos(datos: dict, exp_gastos_len: int, exp_tiempo_len: int, exp_tabla_len: int) -> None:
    df = pd.DataFrame(datos)
    res = procesar_datos_graficas(df)
    
    assert len(res["df_gastos"]) == exp_gastos_len
    assert len(res["df_tiempo"]) == exp_tiempo_len
    assert len(res["df_tabla"]) == exp_tabla_len