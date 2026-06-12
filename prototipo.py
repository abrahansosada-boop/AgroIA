arsenal_veracruz = {
    "maiz_blanco_rolado": {
        "categoria": "energia_almidon",
        "promotor_butirico": True,
        "costo_kg": 6.50
    },
    "sacate_triturado": {
        "categoria": "fibra_fisica",
        "factor_rasgado": True,
        "costo_kg": 1.20
    },
    "melaza": {
        "categoria": "energia_rapida",
        "promotor_butirico": False,
        "costo_kg": 4.00
    },
    "sales_minerales": {
        "categoria": "micronutrientes",
        "promotor_butirico": False,
        "costo_kg": 15.00
    },
    "pasto_estrella": {
        "categoria": "forraje_tropical_base",
        "factor_rasgado": True,
        "costo_kg": 0.50
    },
    "pasto_miyagi": {
        "categoria": "forraje_tropical_elite",
        "factor_rasgado": True,
        "costo_kg": 0.80
    }
}

def auditar_desarrollo_ruminal(edad_meses, dieta_propuesta, base_datos):
    if edad_meses > 6:
        return "Aprobado: Rumen maduro. Restricciones papilares levantadas."

    tiene_almidon = False
    tiene_fibra = False

    for ingrediente in dieta_propuesta:
        datos_ingrediente = base_datos.get(ingrediente)
        
        if datos_ingrediente:
            if datos_ingrediente.get("promotor_butirico") == True:
                tiene_almidon = True
            
            if datos_ingrediente.get("factor_rasgado") == True:
                tiene_fibra = True

    if tiene_almidon and tiene_fibra:
        return "Aprobado: Dieta estimula crecimiento optimo de papilas ruminales."
    else:
        return "Rechazado Critico: Faltan promotores de acido butirico o fibra fisica."

dieta_prueba_1 = ["maiz_blanco_rolado", "sacate_triturado", "melaza"]
resultado_1 = auditar_desarrollo_ruminal(4, dieta_prueba_1, arsenal_veracruz)
print("Prueba 1 (4 meses):", resultado_1)

dieta_prueba_2 = ["melaza", "pasto_miyagi"]
resultado_2 = auditar_desarrollo_ruminal(4, dieta_prueba_2, arsenal_veracruz)
print("Prueba 2 (4 meses):", resultado_2)
def panel_control_precios(base_datos):
    print("\n--- SISTEMA DE ACTUALIZACION DE MERCADO ---")
    objetivo = input("Escriba el nombre del ingrediente a modificar: ").strip()
    
    if objetivo in base_datos:
        precio_viejo = base_datos[objetivo]["costo_kg"]
        nuevo_precio = input(f"El precio actual de {objetivo} es ${precio_viejo}. Ingrese el nuevo precio: ").strip()
        
        base_datos[objetivo]["costo_kg"] = float(nuevo_precio)
        
        print("\nACTUALIZACION CONFIRMADA.")
        print(f"Nuevo registro de {objetivo}: ${base_datos[objetivo]['costo_kg']}")
    else:
        print("\nERROR: El ingrediente no existe en el arsenal.")
def calcular_costo_dieta(dieta_kilos, base_datos):
    costo_total = 0.0

    print("\n--- REPORTE FINANCIERO: DESGLOSE DE LA DIETA ---")

    for ingrediente, kilos in dieta_kilos.items():
        if ingrediente in base_datos:
            precio_unitario = base_datos[ingrediente]["costo_kg"]
            subtotal = precio_unitario * kilos
            costo_total += subtotal

            print(f"- {ingrediente}: {kilos}kg x ${precio_unitario:.2f} = ${subtotal:.2f}")
        else:
            print(f"ALERTA: {ingrediente} no registrado. Fuga de capital posible.")
    print("---------------------------------------------")
    print(f"COSTO TOTAL DIARIO POR ANIMAL: ${costo_total:.2f}")

    return costo_total

dieta_consumo_real = {
    "maiz_blanco_rolado": 1.5,
    "sacate_triturado": 2.0,
    "melaza": 0.5,
    "sales_minerales": 0.05,
}
costo_becerro_hoy = calcular_costo_dieta(dieta_consumo_real, arsenal_veracruz)
def proyeccion_financiera_lote(costo_diario_animal):
    print("\n--- SIMULADOR DE INVERSION A ESCALA ---")

    raza_lote = input("Ingrese el tipo/raza del lote (ej. Holstein, Becerros Engorda): ").strip()
    cabezas = int(input("Ingrese el numero de cabezas: "))
    dias = int(input("Ingrese los dias de duracion del plan (ej. 90 dias para 3 meses): "))

    costo_diario_lote = costo_diario_animal * cabezas
    inversion_total = costo_diario_lote * dias

    print("\n==============================================")
    print(f"REPORTE EJECUTIVO:LOTE {raza_lote.upper()}")
    print(f"Tamano: {cabezas} cabezas | Duracion: {dias} dias")
    print(f"Fuga de Capital Diaria (Rancho): ${costo_diario_lote:,.2f}")
    print(f"INVERSION TOTAL PROYECTADA: ${inversion_total:,.2f}")
    print("==============================================")

proyeccion_financiera_lote(costo_becerro_hoy)
panel_control_precios(arsenal_veracruz)