import pandas as pd

def obtener_historial_bitacora(supabase) -> pd.DataFrame:
    """Extrae la bitácora de la base de datos y la retorna como DataFrame."""
    respuesta = supabase.table("bitacora").select("*").order("fecha", desc=True).execute()
    
    if not respuesta.data:
        return pd.DataFrame()
        
    df = pd.DataFrame(respuesta.data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df
