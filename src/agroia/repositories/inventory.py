def evaluar_alerta_dias(stock: float, consumo_diario: float, limite_critico: int) -> dict:
    """Calcula cuántos días de inventario quedan y retorna su nivel de alerta."""
    dias_restantes = stock / consumo_diario if consumo_diario > 0 else 0.0
    
    if dias_restantes <= limite_critico:
        estado = f"🔴 CRÍTICO ({dias_restantes:.1f} días)"
    elif dias_restantes <= limite_critico + 4:
        estado = f"🟡 PRECAUCIÓN ({dias_restantes:.1f} días)"
    else:
        estado = f"🟢 ÓPTIMO ({dias_restantes:.1f} días)"
        
    return {"dias": dias_restantes, "estado": estado}

def evaluar_alerta_kilos(stock: float, limite_critico: float) -> str:
    """Retorna el nivel de alerta basado estrictamente en el peso (kilos)."""
    if stock <= limite_critico:
        return "🔴 CRÍTICO"
    elif stock <= limite_critico * 2:
        return "🟡 PRECAUCIÓN"
    return "🟢 ÓPTIMO"

def procesar_movimiento_bodega(stock_actual: float, precio_actual: float, kilos_mov: float, tipo_mov: str, nuevo_precio: float = 0.0) -> dict:
    """Procesa ingresos, ajustes y mermas calculando el nuevo stock y el impacto financiero."""
    if kilos_mov <= 0 and "Ajuste" not in tipo_mov:
        return {"exito": False, "error": "Los kilos a mover deben ser mayores a cero."}
        
    nuevo_stock = stock_actual
    precio_final = precio_actual
    perdida = 0.0
    
    if "Ingreso" in tipo_mov:
        nuevo_stock += kilos_mov
        precio_final = nuevo_precio if nuevo_precio > 0 else precio_actual
    elif "Ajuste" in tipo_mov:
        nuevo_stock += kilos_mov 
    elif "Merma" in tipo_mov:
        nuevo_stock -= kilos_mov
        perdida = kilos_mov * precio_actual
        
    return {
        "exito": True,
        "nuevo_stock": nuevo_stock,
        "precio_final": precio_final,
        "perdida_dinero": perdida
    }

def convertir_precio_chicago(precio_dolar: float, precio_centavos_bushel: float) -> float:
    """Convierte el precio del maíz de US cents/bushel a MXN/kg."""
    if precio_centavos_bushel <= 0 or precio_dolar <= 0:
        return 0.0
    precio_usd_bushel = precio_centavos_bushel / 100.0
    precio_usd_kg = precio_usd_bushel / 25.401 # 1 Bushel de Maíz = 25.401 kg
    return round(precio_usd_kg * precio_dolar, 2)