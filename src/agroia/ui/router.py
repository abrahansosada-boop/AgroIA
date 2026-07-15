from agroia.ui.pages.black_box import render_black_box_page
from agroia.ui.pages.dashboard import render_dashboard_page
from agroia.ui.pages.financial_projection import render_financial_projection_page
from agroia.ui.pages.inventory import render_inventory_page
from agroia.ui.pages.laboratory import render_laboratory_page
from agroia.ui.pages.mortality import render_mortality_page
from agroia.ui.pages.resilience_vault import render_resilience_vault_page
from agroia.ui.pages.weight import render_weight_page

ROUTE_DASHBOARD = "Panel Principal"
ROUTE_INVENTORY = "Inventario de Insumos"
ROUTE_LABORATORY = "Súper Laboratorio"
ROUTE_PROJECTION = "Proyección Financiera"
ROUTE_BLACK_BOX = "Caja Negra"
ROUTE_MORTALITY = "Gestión de Mortandad"
ROUTE_WEIGHT = "Control de Peso"
ROUTE_VAULT = "Bóveda"

def render_selected_page(ctx) -> None:
    opcion = ctx.opcion

    if ROUTE_DASHBOARD in opcion:
        render_dashboard_page(ctx)
        
    elif ROUTE_INVENTORY in opcion:
        render_inventory_page(ctx)
        
    elif ROUTE_LABORATORY in opcion:
        render_laboratory_page(ctx)
        
    elif ROUTE_PROJECTION in opcion:
        render_financial_projection_page(ctx)
        
    elif ROUTE_BLACK_BOX in opcion:
        render_black_box_page(ctx)
        
    elif ROUTE_MORTALITY in opcion:
        render_mortality_page(ctx)
        
    elif ROUTE_WEIGHT in opcion:
        render_weight_page(ctx)
        
    elif ROUTE_VAULT in opcion:
        render_resilience_vault_page(ctx)
        
    else:
        render_dashboard_page(ctx)
