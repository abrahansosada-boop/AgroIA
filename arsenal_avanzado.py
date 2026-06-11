import json
import os

arsenal_fabrica = {
    "maiz_blanco_rolado": {"tipo": "energia", "proteina_pct": 8.5, "energia_mcal": 3.1, "costo_kg": 6.50},
    "hoja_de_ebano": {"tipo": "proteina_local", "proteina_pct": 16.0, "energia_mcal": 1.8, "costo_kg": 0.20},
    "sacate_estrella": {"tipo": "fibra_base", "proteina_pct": 7.0, "energia_mcal": 1.9, "costo_kg": 0.50},
    "pasta_de_soya": {"tipo": "proteina_elite", "proteina_pct": 44.0, "energia_mcal": 2.9, "costo_kg": 11.50},
    "melasa": {"tipo": "energia_rapida", "proteina_pct": 3.5, "energia_mcal": 2.5, "costo_kg": 4.00},
    "pollinaza": {"tipo": "nitrogeno_economico", "proteina_pct": 22.0, "energia_mcal": 1.5, "costo_kg": 1.80}
}

ARCHIVO_BD = "memoria_arsenal.json"

def cargar_memoria():
    if os.path.exists(ARCHIVO_BD):
        with open(ARCHIVO_BD, 'r') as archivo:
            return json.load(archivo)
    else:
        guardar_memoria(arsenal_fabrica)
        return arsenal_fabrica

def guardar_memoria(base_datos):
    with open(ARCHIVO_BD, 'w') as archivo:
        json.dump(base_datos, archivo, indent=4)

def consultar_inventario(base_datos):
    print("\n--- INVENTARIO Y VALORES NUTRICIONALES ---")
    for nombre, datos in base_datos.items():
        print(f"[*] {nombre.upper()}")
        print(f"    Costo: ${datos['costo_kg']:.2f} | Proteina: {datos['proteina_pct']}% | Energia: {datos['energia_mcal']} Mcal")

def actualizar_precio(base_datos):
    print("\n--- ACTUALIZACION DE MERCADO ---")
    objetivo = input("Ingrese ingrediente a modificar: ").strip().lower()
    
    if objetivo in base_datos:
        viejo = base_datos[objetivo]["costo_kg"]
        nuevo = input(f"Precio actual de {objetivo} (${viejo:.2f}). Nuevo precio: ").strip()
        base_datos[objetivo]["costo_kg"] = float(nuevo)
        guardar_memoria(base_datos)
        print("MERCADO ACTUALIZADO Y GUARDADO EN DISCO CON EXITO.")
    else:
        print("ERROR: Ingrediente no encontrado.")

def disenar_dieta_big4():
    print("\n--- MODULO DE INTELIGENCIA ---")
    raza = input("1. Raza principal (ej. brahman, angus, holstein): ").strip().lower()
    edad = float(input("2. Edad promedio (meses): "))
    proposito = input("3. Proposito (carne, leche, doble): ").strip().lower()
    clima = float(input("4. Temperatura ambiente actual (C): "))

    meta_proteina = 12.0 
    meta_energia = 2.0   

    if proposito == "leche":
        meta_proteina += 4.0
        meta_energia += 0.8
    elif proposito == "carne":
        meta_proteina += 2.0
        meta_energia += 0.5

    if edad <= 6:
        meta_proteina += 3.0
        
    estres_calorico = False
    if clima > 30:
        if raza not in ["brahman", "gyr", "cebu", "nelore"]:
            estres_calorico = True
            meta_energia += 0.3 

    print("\n" + "="*50)
    print(f" PERFIL METABOLICO REQUERIDO: Lote {raza.capitalize()} ({proposito.capitalize()}) ")
    print("="*50)
    print(f"-> Proteina Cruda Objetivo: {meta_proteina}%")
    print(f"-> Energia Metabolizable Objetivo: {meta_energia} Mcal/kg")
    
    if estres_calorico:
        print("-> [!] ALERTA VETERINARIA: Estres calorico detectado en Bos taurus.")
        print("   Tactica: Aumentar densidad energetica. Reducir forrajes de")
        print("   baja calidad para evitar calor interno por fermentacion.")
    print("="*50)

def auditar_mezcla(base_datos):
    print("\n--- LABORATORIO DE MEZCLAS (MODO EXPERTO) ---")
    print("Escriba 'fin' cuando termine de agregar ingredientes.")
    mezcla = {}
    
    while True:
        ingrediente = input("Ingrediente (o 'fin'): ").strip().lower()
        if ingrediente == 'fin':
            break
        
        if ingrediente in base_datos:
            kilos = float(input(f"Kilos de {ingrediente} a usar: "))
            mezcla[ingrediente] = kilos
        else:
            print("ERROR: Ingrediente no existe en el arsenal.")
            
    if not mezcla:
        print("Operacion abortada. No hay mezcla.")
        return

    total_kilos = sum(mezcla.values())
    total_proteina = 0.0
    total_energia = 0.0
    costo_total = 0.0

    for ing, kg in mezcla.items():
        porcion = kg / total_kilos
        total_proteina += base_datos[ing]["proteina_pct"] * porcion
        total_energia += base_datos[ing]["energia_mcal"] * porcion
        costo_total += base_datos[ing]["costo_kg"] * kg

    print("\n" + "="*50)
    print(f" REPORTE QFB: MEZCLA FINAL ({total_kilos} kg Totales) ")
    print("="*50)
    print(f"-> Proteina Cruda Promedio: {total_proteina:.2f}%")
    print(f"-> Energia Metabolizable Promedio: {total_energia:.2f} Mcal/kg")
    print(f"-> Costo Total de la Mezcla: ${costo_total:.2f}")
    print("="*50)

def recomendar_dieta_automatica(base_datos):
    print("\n--- PILOTO AUTOMATICO: DIETAS PRE-DISEÑADAS ---")
    print("Seleccione el escenario de su rancho:")
    print("[1] Supervivencia / Sequia (Bajo Costo, Forraje Local)")
    print("[2] Engorda Intensiva (Alto Rendimiento, Grano)")
    
    opcion = input("Escenario (1-2): ").strip()
    
    if opcion == "1":
        nombre_dieta = "Fase de Supervivencia"
        receta = {"hoja_de_ebano": 60, "sacate_estrella": 20, "melasa": 15, "pollinaza": 5}
    elif opcion == "2":
        nombre_dieta = "Fase de Engorda Intensiva"
        receta = {"maiz_blanco_rolado": 65, "pasta_de_soya": 15, "sacate_estrella": 15, "melasa": 5}
    else:
        print("ERROR: Opcion no valida.")
        return

    costo_total = 0.0
    proteina_total = 0.0
    
    print("\n" + "="*55)
    print(f" RECETA RECOMENDADA: {nombre_dieta.upper()} (100 kg) ")
    print("="*55)
    
    for ing, kilos in receta.items():
        costo_ing = base_datos[ing]["costo_kg"] * kilos
        costo_total += costo_ing
        proteina_aportada = base_datos[ing]["proteina_pct"] * (kilos / 100)
        proteina_total += proteina_aportada
        
        print(f"-> Mezclar {kilos} kg de {ing.replace('_', ' ').title()} (Costo: ${costo_ing:.2f})")
        
    print("-" * 55)
    print("RESUMEN TECNICO DEL LOTE:")
    print(f"Proteina Cruda Final: {proteina_total:.2f}%")
    print(f"Costo Total (100 kg): ${costo_total:.2f}")
    print(f"Costo por Kg: ${(costo_total/100):.2f}")
    print("="*55)

def iniciar_sistema():
    arsenal_vivo = cargar_memoria()
    
    while True:
        print("\n" + "="*45)
        print(" SISTEMA DE INTELIGENCIA AGROPECUARIA v2.0 ")
        print("="*45)
        print("[1] Consultar Arsenal Quimico")
        print("[2] Actualizar Precios de Mercado")
        print("[3] Disenar Dieta (Big 4)")
        print("[4] Laboratorio de Mezclas (Modo Experto)")
        print("[5] Piloto Automatico (Dietas Recomendadas)")
        print("[6] Apagar Sistema")
        print("="*45)
        
        orden = input("Seleccione una orden (1-6): ").strip()
        
        if orden == "1":
            consultar_inventario(arsenal_vivo)
        elif orden == "2":
            actualizar_precio(arsenal_vivo)
        elif orden == "3":
            disenar_dieta_big4()
        elif orden == "4":
            auditar_mezcla(arsenal_vivo)
        elif orden == "5":
            recomendar_dieta_automatica(arsenal_vivo)
        elif orden == "6":
            print("\nApagando motores... Cambio y fuera.")
            break
        else:
            print("\nERROR: Orden no reconocida. Intente de nuevo.")

iniciar_sistema()