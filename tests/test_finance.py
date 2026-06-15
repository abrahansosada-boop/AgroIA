import pytest
import pandas as pd
from datetime import datetime
from agroia.domain.finance import calcular_kpis_auditoria, procesar_datos_graficas, calcular_proyeccion_financiera, calcular_resumen_panel

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

@pytest.mark.parametrize(
    "peso, prot, costo, precio, tipo, meta, exp_estado",
    [
        # Escenario 1: Alta rentabilidad. Gana $66 libres al día (> $50)
        (200.0, 18.0, 4.0, 90.0, "Tiempo", 6.0, "APROBADO"),
        
        # Escenario 2: Rentabilidad Baja. Gana $38 al día (entre $1 y $49)
        (200.0, 14.0, 5.0, 85.0, "Peso", 300.0, "RIESGO"),
        
        # Escenario 3: Quiebra técnica. Alimento muy caro y precio de carne bajo
        (200.0, 10.0, 15.0, 40.0, "Peso", 300.0, "QUIEBRA"),
    ]
)
def test_calcular_proyeccion_financiera_casos(peso: float, prot: float, costo: float, precio: float, tipo: str, meta: float, exp_estado: str) -> None:
    res = calcular_proyeccion_financiera(peso, prot, costo, precio, tipo, meta)
    assert res["estado_fira"] == exp_estado

@pytest.mark.parametrize(
    "datos, exp_gasto, exp_lotes, exp_costo",
    [
        ({"gasto_total": [100.0, 50.0], "kilos_procesados": [10.0, 5.0]}, 150.0, 2, 10.0), # Caso normal
        ({"gasto_total": [0.0], "kilos_procesados": [0.0]}, 0.0, 0, 0.0), # Lotes sin costo
        ({}, 0.0, 0, 0.0), # Base de datos vacía
    ]
)
def test_calcular_resumen_panel(datos: dict, exp_gasto: float, exp_lotes: int, exp_costo: float) -> None:
    res = calcular_resumen_panel(pd.DataFrame(datos))
    assert res["gasto_real"] == exp_gasto
    assert res["lotes_reales"] == exp_lotes
    assert res["costo_promedio"] == exp_costo