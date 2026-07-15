from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agroia.domain.nutrition import optimizar_dieta_pulp, auditar_mezcla_manual
from agroia.domain.health import calcular_protocolo_sanitario


class CalculoZootecnicoError(ValueError):
    pass


@dataclass(frozen=True)
class ResultadoOptimizacion:
    ingredientes: dict[str, float]
    costo_kg: float
    costo_total_100kg: float
    estado: str
    mensaje: str


def calcular_mezcla(
    ingredientes: dict[str, dict[str, Any]],
    kilos_por_insumo: dict[str, float],
) -> dict[str, Any]:
    """FACADE: Adapta los datos de la UI al cerebro de nutrición."""
    mezcla_formateada = []
    for insumo, kilos in kilos_por_insumo.items():
        if insumo not in ingredientes:
            raise CalculoZootecnicoError(f"Ingredientes sin datos nutricionales: {insumo}")
        mezcla_formateada.append({"kilos": float(kilos), "datos": ingredientes[insumo]})
    
    # Delegamos el cálculo al módulo QFB
    resultado = auditar_mezcla_manual(mezcla_formateada)
    
    if not resultado["exito"]:
        raise CalculoZootecnicoError(resultado["error"])
        
    return {
        "proteina": resultado["proteina"],
        "energia": resultado["energia"],
        "fibra": resultado["fibra"],
        "costo_total": resultado["costo_total"],
        "total_kilos": resultado["total_kilos"],
        "costo_kg": resultado["costo_kg"],
        "detalle": mezcla_formateada,
    }


def validar_inventario_para_receta(
    inventario: dict[str, dict[str, Any]],
    receta: dict[str, float],
) -> list[str]:
    """Se mantiene igual, es puramente validación visual para la UI."""
    errores: list[str] = []
    for insumo, kilos_requeridos in receta.items():
        if insumo not in inventario:
            errores.append(f"{insumo}: no existe en inventario")
            continue
        stock = float(inventario[insumo].get("stock_kg", 0.0))
        if stock <= 0:
            errores.append(f"{insumo}: stock cero")
        elif float(kilos_requeridos) > stock:
            errores.append(
                f"{insumo}: requiere {float(kilos_requeridos):.2f} kg "
                f"y solo hay {stock:.2f} kg"
            )
    return errores


def calcular_dosis_sanitaria(
    peso: float,
    desparasitante: dict[str, Any],
    vacuna: dict[str, Any],
) -> dict[str, float]:
    """FACADE: Conecta la UI con el cerebro farmacológico (mg/kg)."""
    if peso <= 0:
        raise CalculoZootecnicoError("El peso debe ser mayor a cero.")
        
    res = calcular_protocolo_sanitario(peso, desparasitante, vacuna)
    
    return {
        "dosis_desparasitante_ml": float(res["dosis_desparasitante_ml"]),
        "costo_desparasitante": float(res["costo_desparasitante"]),
        "dosis_vacuna_ml": float(res["dosis_vacuna_ml"]),
        "costo_vacuna": float(res["costo_vacuna"]),
        "costo_total": float(res["costo_total"]),
        "retiro_dias": float(res["dias_retiro"]),
    }


def optimizar_dieta(
    base_datos: dict[str, dict[str, Any]],
    req_proteina: float,
    req_energia: float,
    considerar_stock: bool = True,
) -> ResultadoOptimizacion:
    """FACADE: Llama al motor IA con Escudo QFB y formatea para la UI vieja."""
    
    res = optimizar_dieta_pulp(base_datos, req_proteina, req_energia)
    
    if not res["exito"]:
        return ResultadoOptimizacion(
            ingredientes={},
            costo_kg=0.0,
            costo_total_100kg=0.0,
            estado="Inviable",
            mensaje=res["error"]
        )
        
    ingredientes_ui = res["detalles_ia"]["kilos"]
    costo_cien_kg = res["costo_kg"] * 100.0
    
    return ResultadoOptimizacion(
        ingredientes=ingredientes_ui,
        costo_kg=res["costo_kg"],
        costo_total_100kg=costo_cien_kg,
        estado="Optimal",
        mensaje="Fórmula óptima encontrada (Con escudo metabólico activado)."
    )