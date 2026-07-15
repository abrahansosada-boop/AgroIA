from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

ACTIVE_LOT_SESSION_KEY = "perfil"


def build_lot_profile(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "lote_id": row.get("id"),
        "nombre": row["nombre_lote"],
        "raza": row["raza"],
        "genero": row["genero"],
        "proposito": row["proposito"],
        "edad": int(row["edad"]),
        "peso": float(row["peso_promedio"]),
        "clima": float(row["clima_local"]),
        "costo_salud": float(row.get("costo_salud", 0.0)),
    }


def get_active_lot_id(session_state: MutableMapping[str, Any]) -> Any | None:
    profile = session_state.get(ACTIVE_LOT_SESSION_KEY)
    if not isinstance(profile, dict):
        return None
    return profile.get("lote_id")


def get_active_lot_name(session_state: MutableMapping[str, Any]) -> str | None:
    profile = session_state.get(ACTIVE_LOT_SESSION_KEY)
    if not isinstance(profile, dict):
        return None
    name = profile.get("nombre")
    return str(name) if name else None
