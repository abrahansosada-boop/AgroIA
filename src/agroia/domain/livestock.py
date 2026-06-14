from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pulp


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
    total_kilos = sum(float(kilos) for kilos in kilos_por_insumo.values())
    if total_kilos <= 0:
        raise CalculoZootecnicoError("La mezcla debe tener al menos un kilo.")

    faltantes = tuple(
        insumo for insumo in kilos_por_insumo if insumo not in ingredientes
    )
    if faltantes:
        raise CalculoZootecnicoError(
            "Ingredientes sin datos nutricionales: " + ", ".join(faltantes)
        )

    proteina = 0.0
    energia = 0.0
    fibra = 0.0
    costo_total = 0.0
    detalle: list[dict[str, Any]] = []

    for insumo, kilos in kilos_por_insumo.items():
        kilos = float(kilos)
        datos = ingredientes[insumo]
        proteina += kilos * float(datos.get("proteina_pct", 0.0))
        energia += kilos * float(datos.get("energia_mcal", 0.0))
        fibra += kilos * float(datos.get("fibra_pct", 0.0))
        costo = kilos * float(datos.get("costo_kg", 0.0))
        costo_total += costo
        detalle.append({"nombre": insumo, "kilos": kilos, "datos": datos, "costo": costo})

    return {
        "proteina": proteina / total_kilos,
        "energia": energia / total_kilos,
        "fibra": fibra / total_kilos,
        "costo_total": costo_total,
        "total_kilos": total_kilos,
        "costo_kg": costo_total / total_kilos,
        "detalle": detalle,
    }


def validar_inventario_para_receta(
    inventario: dict[str, dict[str, Any]],
    receta: dict[str, float],
) -> list[str]:
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
                f"{insumo}: requiere {float(kilos_requeridos):.2f} kg y solo hay {stock:.2f} kg"
            )
    return errores


def calcular_dosis_sanitaria(
    peso: float,
    desparasitante: dict[str, Any],
    vacuna: dict[str, Any],
) -> dict[str, float]:
    if peso <= 0:
        raise CalculoZootecnicoError("El peso debe ser mayor a cero.")

    dosis_desparasitante_ml = peso * float(desparasitante.get("dosis_ml_por_kg", 0.0))
    costo_desparasitante = dosis_desparasitante_ml * float(
        desparasitante.get("costo_por_ml", 0.0)
    )
    dosis_vacuna_ml = float(vacuna.get("dosis_ml_fija", 0.0))
    costo_vacuna = float(vacuna.get("costo_por_dosis", 0.0))
    retiro_dias = max(
        int(desparasitante.get("tiempo_retiro_dias", 0)),
        int(vacuna.get("tiempo_retiro_dias", 0)),
    )

    return {
        "dosis_desparasitante_ml": dosis_desparasitante_ml,
        "costo_desparasitante": costo_desparasitante,
        "dosis_vacuna_ml": dosis_vacuna_ml,
        "costo_vacuna": costo_vacuna,
        "costo_total": costo_desparasitante + costo_vacuna,
        "retiro_dias": float(retiro_dias),
    }


def optimizar_dieta(
    base_datos: dict[str, dict[str, Any]],
    req_proteina: float,
    req_energia: float,
    considerar_stock: bool = True,
) -> ResultadoOptimizacion:
    insumos = [
        insumo
        for insumo, datos in base_datos.items()
        if not considerar_stock or float(datos.get("stock_kg", 0.0)) > 0
    ]
    if not insumos:
        return ResultadoOptimizacion(
            ingredientes={},
            costo_kg=0.0,
            costo_total_100kg=0.0,
            estado="Sin inventario",
            mensaje="No hay ingredientes con stock disponible.",
        )

    problema = pulp.LpProblem("Dieta_Barata", pulp.LpMinimize)
    variables = pulp.LpVariable.dicts("Ingrediente", insumos, lowBound=0)

    problema += pulp.lpSum(
        variables[i] * float(base_datos[i].get("costo_kg", 0.0)) for i in insumos
    ), "Costo"
    problema += pulp.lpSum(variables[i] for i in insumos) == 100, "Peso_100"
    problema += pulp.lpSum(
        variables[i] * float(base_datos[i].get("proteina_pct", 0.0)) for i in insumos
    ) >= req_proteina * 100, "Req_Prot"
    problema += pulp.lpSum(
        variables[i] * float(base_datos[i].get("energia_mcal", 0.0)) for i in insumos
    ) >= req_energia * 100, "Req_Ener"

    for insumo in insumos:
        datos = base_datos[insumo]
        if "max_pct" in datos:
            problema += variables[insumo] <= float(datos["max_pct"]), f"Max_{insumo}"
        if considerar_stock:
            problema += (
                variables[insumo] <= float(datos.get("stock_kg", 0.0)),
                f"Stock_{insumo}",
            )

    toxicos = [i for i in ["urea_agricola", "pollinaza", "harina_pescado"] if i in insumos]
    if "urea_agricola" in toxicos:
        problema += variables["urea_agricola"] <= 0.5, "Tope_Urea"
    if "pollinaza" in toxicos:
        problema += variables["pollinaza"] <= 12.0, "Tope_Pollinaza"
    if "harina_pescado" in toxicos:
        problema += variables["harina_pescado"] <= 4.0, "Tope_Pescado"
    if len(toxicos) >= 2:
        problema += (
            pulp.lpSum(variables[i] for i in toxicos) <= 11.0,
            "Colchon_Paranoia_Palatabilidad",
        )

    problema.solve(pulp.PULP_CBC_CMD(msg=False))
    estado = pulp.LpStatus[problema.status]
    if estado != "Optimal":
        return ResultadoOptimizacion(
            ingredientes={},
            costo_kg=0.0,
            costo_total_100kg=0.0,
            estado=estado,
            mensaje="No existe una mezcla viable con el inventario y restricciones actuales.",
        )

    receta = {
        insumo: float(variables[insumo].varValue or 0.0)
        for insumo in insumos
        if float(variables[insumo].varValue or 0.0) > 0.01
    }
    costo_total = sum(
        kilos * float(base_datos[insumo].get("costo_kg", 0.0))
        for insumo, kilos in receta.items()
    )
    return ResultadoOptimizacion(
        ingredientes=receta,
        costo_kg=costo_total / 100,
        costo_total_100kg=costo_total,
        estado=estado,
        mensaje="Formula optima encontrada.",
    )
