from demo_supabase import DemoSupabaseClient, cargar_base_demo


def test_demo_client_select_update_insert_order() -> None:
    client = DemoSupabaseClient()

    inventario = client.table("inventario").select("*").execute().data
    assert any(row["insumo"] == "maiz_molido" for row in inventario)

    client.table("inventario").update({"stock_kg": 123.0}).eq(
        "insumo", "maiz_molido"
    ).execute()
    maiz = client.table("inventario").select("*").eq("insumo", "maiz_molido").execute().data
    assert maiz[0]["stock_kg"] == 123.0

    client.table("bitacora").insert(
        {
            "fecha": "2026-06-12T12:00:00",
            "accion": "Prueba",
            "detalle": "Movimiento demo",
            "gasto_total": 10,
            "kilos_procesados": 20,
        }
    ).execute()
    bitacora = client.table("bitacora").select("*").order("fecha", desc=True).execute().data
    assert bitacora[0]["accion"] == "Prueba"


def test_cargar_base_demo_agrega_stock_realista() -> None:
    base = cargar_base_demo()

    assert base["maiz_molido"]["stock_kg"] > 0
    assert base["pasta_de_soya"]["stock_kg"] > 0
