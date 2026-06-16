from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol


class DatabaseClient(Protocol):
    def table(self, name: str) -> Any: ...

DEFAULT_TENANT_ID = "demo-rancho"
TENANT_SCOPED_TABLES = {
    "inventario",
    "bitacora",
    "perfiles_lotes",
    "lotes",
}


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    ADVISOR = "advisor"
    OPERATOR = "operator"


@dataclass(frozen=True)
class UserContext:
    tenant_id: str
    tenant_name: str
    user_id: str
    display_name: str
    role: Role

    @property
    def can_manage_costs(self) -> bool:
        return self.role in {Role.OWNER, Role.ADMIN}

    @property
    def can_configure_tenant(self) -> bool:
        return self.role is Role.OWNER

    @property
    def can_create_recommendations(self) -> bool:
        return self.role in {Role.OWNER, Role.ADMIN, Role.ADVISOR}

    @property
    def can_record_operations(self) -> bool:
        return self.role in {Role.OWNER, Role.ADMIN, Role.OPERATOR}


def resolve_user_context(
    db: DatabaseClient,
    session_state: MutableMapping[str, Any],
) -> UserContext:
    stored = session_state.get("agroia_user_context")
    if isinstance(stored, UserContext):
        return stored

    context = _load_first_active_user_context(db)
    session_state["agroia_user_context"] = context
    return context


def _load_first_active_user_context(db: DatabaseClient) -> UserContext:
    try:
        memberships = (
            db.table("tenant_memberships")
            .select("*")
            .eq("is_active", True)
            .execute()
            .data
        )
        tenants = db.table("tenants").select("*").execute().data
    except Exception:
        return _default_demo_context()

    if not memberships:
        return _default_demo_context()

    membership = memberships[0]
    role = _coerce_role(membership.get("role"))
    tenant_id = str(membership.get("tenant_id") or DEFAULT_TENANT_ID)
    tenant = next((item for item in tenants if item.get("id") == tenant_id), {})

    return UserContext(
        tenant_id=tenant_id,
        tenant_name=str(tenant.get("name") or "Rancho demo"),
        user_id=str(membership.get("user_id") or "demo-owner"),
        display_name=str(membership.get("display_name") or "Owner demo"),
        role=role,
    )


def _coerce_role(value: Any) -> Role:
    try:
        return Role(str(value))
    except ValueError:
        return Role.OPERATOR


def _default_demo_context() -> UserContext:
    return UserContext(
        tenant_id=DEFAULT_TENANT_ID,
        tenant_name="Rancho demo",
        user_id="demo-owner",
        display_name="Owner demo",
        role=Role.OWNER,
    )


class TenantScopedDatabaseClient:
    def __init__(self, db: DatabaseClient, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def table(self, name: str) -> Any:
        table = self._db.table(name)
        if name not in TENANT_SCOPED_TABLES:
            return table
        return TenantScopedTable(table, self._tenant_id)


class TenantScopedTable:
    def __init__(self, table: Any, tenant_id: str) -> None:
        self._table = table
        self._tenant_id = tenant_id

    def select(self, *columns: str) -> Any:
        return self._table.select(*columns).eq("tenant_id", self._tenant_id)

    def insert(self, payload: dict[str, Any]) -> Any:
        scoped_payload = dict(payload)
        scoped_payload.setdefault("tenant_id", self._tenant_id)
        return self._table.insert(scoped_payload)

    def update(self, payload: dict[str, Any]) -> Any:
        return self._table.update(payload).eq("tenant_id", self._tenant_id)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._table, name)
