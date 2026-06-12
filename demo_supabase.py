from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any


DEMO_INVENTORY: dict[str, dict[str, float]] = {
    "maiz_molido": {"stock_kg": 1800.0, "costo_kg": 3.6},
    "pasta_de_soya": {"stock_kg": 420.0, "costo_kg": 11.2},
    "salvado_trigo": {"stock_kg": 650.0, "costo_kg": 4.4},
    "rastrojo_maiz": {"stock_kg": 1200.0, "costo_kg": 1.3},
    "pollinaza": {"stock_kg": 500.0, "costo_kg": 2.1},
    "melaza_cana": {"stock_kg": 300.0, "costo_kg": 4.2},
    "premezcla_mineral": {"stock_kg": 90.0, "costo_kg": 24.0},
}


DEMO_LOTES: list[dict[str, Any]] = [
    {
        "nombre_lote": "Demo becerros desarrollo",
        "raza": "brahman",
        "genero": "Macho",
        "proposito": "Carne",
        "edad": 8,
        "peso_promedio": 240.0,
        "clima_local": 32.0,
        "costo_salud": 0.0,
    }
]


DEMO_BITACORA: list[dict[str, Any]] = [
    {
        "fecha": "2026-06-12T09:00:00",
        "accion": "Carga demo",
        "detalle": "Datos locales de ejemplo cargados sin Supabase real.",
        "gasto_total": 0.0,
        "kilos_procesados": 0.0,
    }
]


@dataclass
class DemoResult:
    data: list[dict[str, Any]]


class DemoTableQuery:
    def __init__(self, table_rows: list[dict[str, Any]]) -> None:
        self._rows = table_rows
        self._operation = "select"
        self._payload: dict[str, Any] | None = None
        self._filters: list[tuple[str, Any]] = []
        self._order_column: str | None = None
        self._order_desc = False

    def select(self, *_columns: str) -> "DemoTableQuery":
        self._operation = "select"
        return self

    def insert(self, payload: dict[str, Any]) -> "DemoTableQuery":
        self._operation = "insert"
        self._payload = payload
        return self

    def update(self, payload: dict[str, Any]) -> "DemoTableQuery":
        self._operation = "update"
        self._payload = payload
        return self

    def eq(self, column: str, value: Any) -> "DemoTableQuery":
        self._filters.append((column, value))
        return self

    def order(self, column: str, desc: bool = False) -> "DemoTableQuery":
        self._order_column = column
        self._order_desc = desc
        return self

    def execute(self) -> DemoResult:
        if self._operation == "insert":
            row = dict(self._payload or {})
            row.setdefault("fecha", datetime.now().isoformat(timespec="seconds"))
            self._rows.append(row)
            return DemoResult([deepcopy(row)])

        matched_rows = [row for row in self._rows if self._matches(row)]

        if self._operation == "update":
            for row in matched_rows:
                row.update(self._payload or {})
            return DemoResult(deepcopy(matched_rows))

        if self._order_column:
            matched_rows = sorted(
                matched_rows,
                key=lambda row: row.get(self._order_column) or "",
                reverse=self._order_desc,
            )
        return DemoResult(deepcopy(matched_rows))

    def _matches(self, row: dict[str, Any]) -> bool:
        return all(row.get(column) == value for column, value in self._filters)


class DemoSupabaseClient:
    def __init__(self) -> None:
        self._tables = {
            "inventario": [
                {"insumo": insumo, **datos}
                for insumo, datos in DEMO_INVENTORY.items()
            ],
            "perfiles_lotes": deepcopy(DEMO_LOTES),
            "bitacora": deepcopy(DEMO_BITACORA),
        }

    def table(self, name: str) -> DemoTableQuery:
        self._tables.setdefault(name, [])
        return DemoTableQuery(self._tables[name])


def cargar_base_demo(path: str | Path = "bd_agro_v2.json") -> dict[str, dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as archivo:
        base_datos = json.load(archivo)

    for insumo, valores in DEMO_INVENTORY.items():
        if insumo in base_datos:
            base_datos[insumo].update(valores)

    return base_datos
