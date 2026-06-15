import pandas as pd

def calcular_kpis_auditoria(df_bitacora: pd.DataFrame) -> dict:
    """Calcula métricas financieras reales basadas en los datos de la base de datos."""
    if df_bitacora.empty or 'gasto_total' not in df_bitacora.columns:
        return {"gasto_total": 0.0, "total_movimientos": 0}
        
    return {
        "gasto_total": float(df_bitacora['gasto_total'].sum()),
        "total_movimientos": len(df_bitacora)
    }

def procesar_datos_graficas(df_bitacora: pd.DataFrame) -> dict:
    """Filtra y agrupa el DataFrame crudo para alimentar las gráficas de Streamlit."""
    if df_bitacora.empty:
        return {"df_gastos": pd.DataFrame(), "df_tiempo": pd.DataFrame(), "df_tabla": pd.DataFrame()}
    
    df_gastos = df_bitacora[df_bitacora.get('gasto_total', 0) > 0].copy()
    
    if not df_gastos.empty:
        df_tiempo = df_gastos.groupby(df_gastos['fecha'].dt.date)['gasto_total'].sum().reset_index()
    else:
        df_tiempo = pd.DataFrame()
    
    df_tabla = df_bitacora.copy()
    df_tabla['fecha_str'] = df_tabla['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    if 'detalle' in df_tabla.columns and 'accion' in df_tabla.columns:
        df_tabla = df_tabla[['fecha_str', 'accion', 'detalle']]
        df_tabla.columns = ['Fecha y Hora', 'Tipo de Acción', 'Detalle del Movimiento']
        
    return {
        "df_gastos": df_gastos,
        "df_tiempo": df_tiempo,
        "df_tabla": df_tabla
    }

def calcular_proyeccion_financiera(peso_actual: float, proteina_dieta: float, costo_dieta_kg: float, precio_venta_kg: float, tipo_meta: str, meta_obj: float) -> dict:
    """Calcula proyecciones de engorda, conversión alimenticia y márgenes de rentabilidad."""
    ganancia_est = round(0.8 + ((proteina_dieta - 14.0) * 0.05), 2)
    if ganancia_est <= 0:
        ganancia_est = 0.1  
        
    consumo_diario = peso_actual * 0.03
    costo_dia = consumo_diario * costo_dieta_kg
    costo_kg_carne = costo_dia / ganancia_est if ganancia_est > 0 else 0.0
    
    ingreso_bruto_diario = ganancia_est * precio_venta_kg
    ganancia_neta_diaria = ingreso_bruto_diario - costo_dia
    margen_por_kilo = precio_venta_kg - costo_kg_carne
    
    dias_faltantes = 0.0
    peso_final_proy = peso_actual
    
    if "Peso" in tipo_meta:
        if meta_obj > peso_actual:
            dias_faltantes = (meta_obj - peso_actual) / ganancia_est
    else:
        peso_final_proy = peso_actual + ((meta_obj * 30) * ganancia_est)
        
    if ganancia_neta_diaria >= 50:
        estado_fira = "APROBADO"
    elif ganancia_neta_diaria > 0:
        estado_fira = "RIESGO"
    else:
        estado_fira = "QUIEBRA"
        
    return {
        "ganancia_est": ganancia_est,
        "costo_kg_carne": costo_kg_carne,
        "ganancia_neta_diaria": ganancia_neta_diaria,
        "margen_por_kilo": margen_por_kilo,
        "dias_faltantes": dias_faltantes,
        "peso_final_proy": peso_final_proy,
        "estado_fira": estado_fira
    }

def calcular_resumen_panel(df_finanzas: pd.DataFrame) -> dict:
    """Calcula los KPIs del dashboard principal."""
    if df_finanzas.empty or 'gasto_total' not in df_finanzas.columns:
        return {"gasto_real": 0.0, "lotes_reales": 0, "costo_promedio": 0.0}
        
    gasto_real = float(df_finanzas['gasto_total'].sum())
    lotes_reales = len(df_finanzas[df_finanzas['gasto_total'] > 0])
    
    kilos_totales = float(df_finanzas.get('kilos_procesados', pd.Series(dtype=float)).sum())
    costo_promedio = (gasto_real / kilos_totales) if kilos_totales > 0 else 0.0
    
    return {
        "gasto_real": gasto_real,
        "lotes_reales": lotes_reales,
        "costo_promedio": costo_promedio
    }