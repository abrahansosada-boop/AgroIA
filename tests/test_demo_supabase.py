from agroia.demo_supabase import DEMO_INVENTORY, DEMO_TENANT_ID, DemoSupabaseClient
from agroia.tenancy import TenantScopedDatabaseClient


def test_reads_seeded_inventory() -> None:
    client = DemoSupabaseClient()

    result = client.table("inventario").select("*").execute()

    assert len(result.data) == len(DEMO_INVENTORY)
    assert result.data[0]["insumo"] in DEMO_INVENTORY


def test_updates_only_filtered_rows() -> None:
    client = DemoSupabaseClient()

    result = (
        client.table("inventario")
        .update({"stock_kg": 25.0})
        .eq("insumo", "maiz_molido")
        .execute()
    )

    assert result.data == [
        {
            "tenant_id": DEMO_TENANT_ID,
            "insumo": "maiz_molido",
            "stock_kg": 25.0,
            "costo_kg": 3.6,
        }
    ]
    inventory = client.table("inventario").select("*").execute().data
    assert sum(row["stock_kg"] == 25.0 for row in inventory) == 1


def test_inserts_rows_with_timestamp_and_orders_them() -> None:
    client = DemoSupabaseClient()

    inserted = (
        client.table("bitacora")
        .insert({"accion": "Nueva", "detalle": "Demo"})
        .execute()
    )
    ordered = (
        client.table("bitacora")
        .select("*")
        .order("fecha", desc=True)
        .execute()
    )

    assert inserted.data[0]["fecha"]
    assert ordered.data[0]["accion"] == "Nueva"


def test_results_are_defensive_copies() -> None:
    client = DemoSupabaseClient()

    result = client.table("inventario").select("*").execute()
    result.data[0]["stock_kg"] = -1

    fresh_result = client.table("inventario").select("*").execute()
    assert fresh_result.data[0]["stock_kg"] != -1


def test_scoped_client_filters_rows_by_tenant_and_scopes_inserts() -> None:
    client = DemoSupabaseClient()
    other_tenant = "rancho-ajeno"
    client.table("inventario").insert(
        {
            "tenant_id": other_tenant,
            "insumo": "maiz_molido",
            "stock_kg": 999.0,
            "costo_kg": 1.0,
        }
    ).execute()

    scoped = TenantScopedDatabaseClient(client, DEMO_TENANT_ID)
    inventory = scoped.table("inventario").select("*").execute().data
    scoped.table("bitacora").insert({"accion": "Nueva", "detalle": "Demo"}).execute()
    bitacora = scoped.table("bitacora").select("*").execute().data

    assert all(row["tenant_id"] == DEMO_TENANT_ID for row in inventory)
    assert all(row["tenant_id"] == DEMO_TENANT_ID for row in bitacora)
    assert len(inventory) == len(DEMO_INVENTORY)
