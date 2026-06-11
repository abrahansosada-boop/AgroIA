import json
import os

arsenal_fabrica = {
    "maiz_blanco": {"tipo": "energia", "proteina_pct": 8.5, "energia_mcal": 3.1, "fibra_pct": 10.0, "costo_kg": 6.50},
    "sorgo": {"tipo": "energia", "proteina_pct": 9.0, "energia_mcal": 3.0, "fibra_pct": 12.0, "costo_kg": 5.50},
    "trigo": {"tipo": "energia", "proteina_pct": 12.0, "energia_mcal": 3.2, "fibra_pct": 14.0, "costo_kg": 7.00},
    "avena": {"tipo": "energia", "proteina_pct": 11.0, "energia_mcal": 2.9, "fibra_pct": 28.0, "costo_kg": 8.00},
    "cebada": {"tipo": "energia", "proteina_pct": 11.5, "energia_mcal": 3.0, "fibra_pct": 19.0, "costo_kg": 6.80},
    "pasta_de_soya": {"tipo": "proteina", "proteina_pct": 44.0, "energia_mcal": 2.9, "fibra_pct": 15.0, "costo_kg": 11.50},
    "pasta_de_canola": {"tipo": "proteina", "proteina_pct": 36.0, "energia_mcal": 2.6, "fibra_pct": 25.0, "costo_kg": 9.00},
    "salvado_de_trigo": {"tipo": "fibra", "proteina_pct": 15.0, "energia_mcal": 2.5, "fibra_pct": 45.0, "costo_kg": 5.00},
    "melasa": {"tipo": "energia_rapida", "proteina_pct": 3.5, "energia_mcal": 2.5, "fibra_pct": 0.0, "costo_kg": 4.00},
    "pulpa_citrica": {"tipo": "energia", "proteina_pct": 6.5, "energia_mcal": 2.8, "fibra_pct": 25.0, "costo_kg": 2.50},
    "alfalfa": {"tipo": "forraje", "proteina_pct": 18.0, "energia_mcal": 2.2, "fibra_pct": 40.0, "costo_kg": 6.00},
    "zacate_estrella": {"tipo": "forraje", "proteina_pct": 7.0, "energia_mcal": 1.9, "fibra_pct": 70.0, "costo_kg": 0.50},
    "zacate_buffel": {"tipo": "forraje", "proteina_pct": 8.0, "energia_mcal": 1.8, "fibra_pct": 75.0, "costo_kg": 0.60},
    "hoja_de_ebano": {"tipo": "proteina_local", "proteina_pct": 16.0, "energia_mcal": 1.8, "fibra_pct": 45.0, "costo_kg": 0.20},
    "pollinaza": {"tipo": "nitrogeno", "proteina_pct": 22.0, "energia_mcal": 1.5, "fibra_pct": 30.0, "costo_kg": 1.80}
}

ARCHIVO_BD = "memoria_arsenal.json"

atlas_animales = {
    "brahman": {"tronco": "indicus", "clima_ideal": "tropico", "resistencia_calor": 1.0},
    "nelore": {"tronco": "indicus", "clima_ideal": "tropico", "resistencia_calor": 1.0},
    "gyr": {"tronco": "indicus", "clima_ideal": "tropico", "resistencia_calor": 1.0},
    "guzerat": {"tronco": "indicus", "clima_ideal": "tropico", "resistencia_calor": 1.0},
    "angus": {"tronco": "taurus", "clima_ideal": "templado", "resistencia_calor": 0.4},
    "hereford": {"tronco": "taurus", "clima_ideal": "templado", "resistencia_calor": 0.4},
    "charolais": {"tronco": "taurus", "clima_ideal": "templado", "resistencia_calor": 0.5},
    "simmental": {"tronco": "taurus", "clima_ideal": "templado", "resistencia_calor": 0.5},
    "holstein": {"tronco": "taurus", "clima_ideal": "templado", "resistencia_calor": 0.3},
    "jersey": {"tronco": "taurus", "clima_ideal": "templado", "resistencia_calor": 0.4},
    "brangus": {"tronco": "sintetico", "clima_ideal": "adaptable", "resistencia_calor": 0.8},
    "simbrah": {"tronco": "sintetico", "clima_ideal": "adaptable", "resistencia_calor": 0.8},
    "suizo_americano": {"tronco": "sintetico", "clima_ideal": "adaptable", "resistencia_calor": 0.7}
}
import json

arsenal_fabrica = {
    "maiz_blanco": {"tipo": "energia", "proteina_pct": 8.5, "energia_mcal": 3.1, "fibra_pct": 10.0, "costo_kg": 6.50},
    "sorgo": {"tipo": "energia", "proteina_pct": 9.0, "energia_mcal": 3.0, "fibra_pct": 12.0, "costo_kg": 5.50},
    "trigo": {"tipo": "energia", "proteina_pct": 12.0, "energia_mcal": 3.2, "fibra_pct": 14.0, "costo_kg": 7.00},
    "avena": {"tipo": "energia", "proteina_pct": 11.0, "energia_mcal": 2.9, "fibra_pct": 28.0, "costo_kg": 8.00},
    "cebada": {"tipo": "energia", "proteina_pct": 11.5, "energia_mcal": 3.0, "fibra_pct": 19.0, "costo_kg": 6.80},
    "pasta_de_soya": {"tipo": "proteina", "proteina_pct": 44.0, "energia_mcal": 2.9, "fibra_pct": 15.0, "costo_kg": 11.50},
    "pasta_de_canola": {"tipo": "proteina", "proteina_pct": 36.0, "energia_mcal": 2.6, "fibra_pct": 25.0, "costo_kg": 9.00},
    "salvado_de_trigo": {"tipo": "fibra", "proteina_pct": 15.0, "energia_mcal": 2.5, "fibra_pct": 45.0, "costo_kg": 5.00},
    "melasa": {"tipo": "energia_rapida", "proteina_pct": 3.5, "energia_mcal": 2.5, "fibra_pct": 0.0, "costo_kg": 4.00},
    "pulpa_citrica": {"tipo": "energia", "proteina_pct": 6.5, "energia_mcal": 2.8, "fibra_pct": 25.0, "costo_kg": 2.50},
    "alfalfa": {"tipo": "forraje", "proteina_pct": 18.0, "energia_mcal": 2.2, "fibra_pct": 40.0, "costo_kg": 6.00},
    "zacate_estrella": {"tipo": "forraje", "proteina_pct": 7.0, "energia_mcal": 1.9, "fibra_pct": 70.0, "costo_kg": 0.50},
    "zacate_buffel": {"tipo": "forraje", "proteina_pct": 8.0, "energia_mcal": 1.8, "fibra_pct": 75.0, "costo_kg": 0.60},
    "hoja_de_ebano": {"tipo": "proteina_local", "proteina_pct": 16.0, "energia_mcal": 1.8, "fibra_pct": 45.0, "costo_kg": 0.20},
    "pollinaza": {"tipo": "nitrogeno", "proteina_pct": 22.0, "energia_mcal": 1.5, "fibra_pct": 30.0, "costo_kg": 1.80}
}

def cargar_memoria():
    try:
        with open("bd_agro_v2.json", "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        with open("bd_agro_v2.json", "w") as archivo:
            json.dump(arsenal_fabrica, archivo, indent=4)
        return arsenal_fabrica

def guardar_memoria(base_datos):
    with open(ARCHIVO_BD, 'w') as archivo:
        json.dump(base_datos, archivo, indent=4)

def consultar_inventario(base_datos):
    print("\n--- INVENTARIO Y VALORES NUTRICIONALES ---")
    for nombre, datos in base_datos.items():
        print(f"[*] {nombre.upper().replace('_', ' ')}")
        print(f"    Costo: ${datos['costo_kg']:.2f} | P: {datos['proteina_pct']}% | E: {datos['energia_mcal']} Mcal | Fibra: {datos['fibra_pct']}%")

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

def diseñar_dieta():
    print("\n--- MODULO DE INTELIGENCIA (V2.5) ---")
    estres_calorico = False
    
    raza = input("1. Raza principal: ").strip().lower()
    genero = input("2. Genero (macho/hembra): ").strip().lower()
    edad = float(input("3. Edad promedio (meses): "))
    proposito = input("4. Proposito (carne, leche, doble, semental): ").strip().lower()
    clima = float(input("5. Temperatura ambiente actual (C): "))
    peso = float(input("6. Peso vivo estimado actual (kg): "))
    meta_proteina = 11.0 
    meta_energia = 1.9   

    # Lógica de Género y Propósito
    if genero == "macho":
        if proposito == "semental":
            meta_proteina += 3.0
            meta_energia += 0.4
        else:
            meta_proteina += 1.5
            meta_energia += 0.6
    else:
        if proposito == "leche":
            meta_proteina += 5.0
            meta_energia += 0.9
        elif proposito == "reemplazo":
            meta_proteina += 2.0

    if edad <= 7:
        meta_proteina += 4.0
        meta_energia += 0.2

    if raza in atlas_animales:
        datos_raza = atlas_animales[raza]
        tronco = datos_raza["tronco"]
        clima_ideal = datos_raza["clima_ideal"]
        
        if clima > 30:
            if clima_ideal == "templado":
                estres_calorico = True
                meta_energia += 0.4 # Castigo energético por jadeo severo
                print(f"-> [!] ALERTA CRITICA: {raza.upper()} no es para este clima.")
            elif clima_ideal == "adaptable":
                estres_calorico = True
                meta_energia += 0.2 
    else:
        print(f"ADVERTENCIA: Raza {raza} no mapeada. Usando valores estandar.")
        if clima > 30: estres_calorico = True

    print("\n" + "="*50)
    print(f" REQUERIMIENTO: {raza.upper()} | {clima}C | {proposito.upper()} ")
    print("="*50)
    print(f"-> Proteina Cruda: {meta_proteina}%")
    print(f"-> Energia: {meta_energia} Mcal/kg")
    
    if estres_calorico:
        print("-> [!] ALERTA: Mitigar calor. Evaluar sombra y densidad.")
    print("="*50)
    
    return {"meta_p": meta_proteina, "meta_e": meta_energia, "peso": peso}

def auditar_mezcla(base_datos):
    print("\n--- LABORATORIO DE MEZCLAS (MODULO DE RIESGOS) ---")
    mezcla_total = {}
    total_kilos = 0.0
    
    while True:
        ingrediente = input("Ingrediente (o 'fin'): ").strip().lower()
        if ingrediente == "fin": break
        
        if ingrediente in base_datos:
            kilos = float(input(f"Kilos de {ingrediente}: "))
            mezcla_total[ingrediente] = kilos
            total_kilos += kilos
        else:
            print("ERROR: Ingrediente no existe en el arsenal.")

    if total_kilos == 0:
        print("Operacion abortada. No hay mezcla.")
        return None

    # CALCULOS DE NUTRICION Y RIESGOS
    proteina_acumulada = 0.0
    energia_acumulada = 0.0
    fibra_acumulada = 0.0
    costo_total = 0.0

    print("\n--- ANALISIS DE RIESGOS ---")
    for ing, k in mezcla_total.items():
        pct_en_dieta = (k / total_kilos) * 100
        datos = base_datos[ing]
        
        # --- BLOQUE DE SEGURIDAD ---
        if ing == "pollinaza" and pct_en_dieta > 15:
            print(f"[⚠️ RIESGO] Pollinaza al {pct_en_dieta:.1f}%: ¡Muy alto! Riesgo de intoxicación.")
        if ing == "melasa" and pct_en_dieta > 10:
            print(f"[⚠️ RIESGO] Melaza al {pct_en_dieta:.1f}%: Puede causar diarreas.")
        if (ing == "maiz_blanco" or ing == "sorgo") and pct_en_dieta > 70:
            print(f"[⚠️ RIESGO] Granos al {pct_en_dieta:.1f}%: Riesgo de Acidosis Ruminal.")

        # --- ACUMULADORES DE VALOR ---
        porcion = k / total_kilos
        proteina_acumulada += datos["proteina_pct"] * porcion
        energia_acumulada += datos["energia_mcal"] * porcion
        fibra_acumulada += datos["fibra_pct"] * porcion
        costo_total += datos["costo_kg"] * k

    print("\n" + "="*50)
    print(f" REPORTE: MEZCLA FINAL ({total_kilos} kg Totales) ")
    print("="*50)
    print(f"-> Proteina Cruda Promedio: {proteina_acumulada:.2f}%")
    print(f"-> Energia Metabolizable Promedio: {energia_acumulada:.2f} Mcal/kg")
    print(f"-> Fibra (FDN) Promedio: {fibra_acumulada:.2f}%")
    print(f"-> Costo Total de la Mezcla: ${costo_total:.2f}")
    print("="*50)

    costo_por_kg = costo_total / total_kilos

    return {
        "proteina": proteina_acumulada, 
        "energia": energia_acumulada, 
        "fibra": fibra_acumulada,
        "costo_kg": costo_por_kg,
        "total_kilos": total_kilos
    }

def recomendar_dieta_automatica(base_datos):
    print("\n--- PILOTO AUTOMATICO: DIETAS PRE-DISEÑADAS ---")
    print("Seleccione el escenario de su rancho:")
    print("[1] Supervivencia / Sequia (Bajo Costo, Forraje Local)")
    print("[2] Engorda Intensiva (Alto Rendimiento, Grano)")
    
    opcion = input("Escenario (1-2): ").strip()
    
    if opcion == "1":
        nombre_dieta = "Fase de Supervivencia"
        receta = {"hoja_de_ebano": 60, "zacate_estrella": 20, "melasa": 15, "pollinaza": 5}
    elif opcion == "2":
        nombre_dieta = "Fase de Engorda Intensiva"
        receta = {"maiz_blanco": 65, "pasta_de_soya": 15, "zacate_buffel": 15, "melasa": 5}
    else:
        print("ERROR: Opcion no valida.")
        return

    costo_total = 0.0
    proteina_total = 0.0
    
    print("\n" + "="*55)
    print(f" RECETA RECOMENDADA: {nombre_dieta.upper()} (100 kg)")
    print("="*55)
    
    for ing, kilos in receta.items():
        if ing in base_datos:
            costo_ing = base_datos[ing]["costo_kg"] * kilos
            costo_total += costo_ing
            # Calculo de proteina aportada por este ingrediente
            proteina_aportada = base_datos[ing]["proteina_pct"] * (kilos / 100)
            proteina_total += proteina_aportada
            print(f"-> Mezclar {kilos} kg de {ing.replace('_', ' ').title()} (Costo: ${costo_ing:.2f})")
    
    print("-" * 55)
    print(f"RESUMEN TECNICO DEL LOTE:")
    print(f"Proteina Cruda Final: {proteina_total:.2f}%")
    print(f"Costo Total (100 kg): ${costo_total:.2f}")
    print(f"Costo por Kg: ${costo_total/100:.2f}")
    print("="*55)
def calcular_ganancia_pro(perfil, mezcla):
    if perfil is None or mezcla is None:
        print("\n[!] ERROR PRO: Faltan datos (Pase por la Opcion 3 y 4 primero).")
        return

    print("\n--- PROYECCION DE GANANCIA Y RENTABILIDAD ---")
    delta_p = mezcla["proteina"] - perfil["meta_p"]
    delta_e = mezcla["energia"] - perfil["meta_e"]
    ganancia = 0.8 + (delta_p * 0.05) + (delta_e * 0.2)
    
    fibra = mezcla["fibra"]
    if fibra < 15.0: ganancia -= 0.5
    elif fibra > 60.0: ganancia -= 0.3
    ganancia = max(0.1, min(2.5, ganancia))

    #MATEMATICA FINANCIERA
    peso_animal = perfil["peso"]
    consumo_diario_kg = peso_animal * 0.03 
    costo_diario = consumo_diario_kg * mezcla["costo_kg"]
    costo_por_kilo_producido = costo_diario / ganancia
    dias_duracion = mezcla["total_kilos"] / consumo_diario_kg # <-- NUEVO

    print("="*50)
    print(f"Ganancia Diaria Esperada : {ganancia:.3f} kg/dia")
    print(f"Consumo Diario Estimado  : {consumo_diario_kg:.1f} kg de mezcla")
    print(f"Duracion del Lote Preparado: {dias_duracion:.1f} dias") # <-- NUEVO
    print(f"Costo de Alimentacion    : ${costo_diario:.2f} MXN diarios")
    print(f"-> COSTO POR KG PRODUCIDO: ${costo_por_kilo_producido:.2f} MXN <-")
    print("="*50)

    #GENERADOR DE REPORTE
    guardar = input("\n¿Desea generar el Reporte de Auditoria en TXT? (s/n): ").strip().lower()
    if guardar == 's':
        try:
            with open("Reporte_Lote.txt", "w") as archivo:
                archivo.write("=== REPORTE DE AUDITORIA AGROPECUARIA ===\n")
                archivo.write(f"Peso del animal evaluado : {peso_animal} kg\n")
                archivo.write(f"Proteina de la mezcla    : {mezcla['proteina']:.2f}%\n")
                archivo.write(f"Energia de la mezcla     : {mezcla['energia']:.2f} Mcal\n")
                archivo.write(f"Fibra (FDN)              : {mezcla['fibra']:.2f}%\n")
                archivo.write(f"Ganancia Proyectada      : {ganancia:.3f} kg/dia\n")
                archivo.write(f"Consumo Diario           : {consumo_diario_kg:.1f} kg\n")
                archivo.write(f"Duracion de la Mezcla    : {dias_duracion:.1f} dias\n") # <-- NUEVO
                archivo.write(f"Costo por Kg Producido   : ${costo_por_kilo_producido:.2f}\n")
                archivo.write("=========================================\n")
            print("[+] Reporte 'Reporte_Lote.txt' guardado exitosamente.")
        except Exception as e:
            print(f"[!] Error: {e}")

    print("="*50)
    print(f"Ganancia Diaria Esperada : {ganancia:.3f} kg/dia")
    print(f"Consumo Diario Estimado  : {consumo_diario_kg:.1f} kg de mezcla")
    print(f"Costo de Alimentacion    : ${costo_diario:.2f} MXN diarios")
    print(f"-> COSTO POR KG PRODUCIDO: ${costo_por_kilo_producido:.2f} MXN <-")
    print("="*50)

    #GENERADOR DE REPORTE (A DEMANDA)
    guardar = input("\n¿Desea generar el Reporte de Auditoria en TXT? (s/n): ").strip().lower()
    if guardar == 's':
        try:
            with open("Reporte_Lote.txt", "w") as archivo:
                archivo.write("=== REPORTE DE AUDITORIA AGROPECUARIA ===\n")
                archivo.write(f"Peso del animal evaluado : {peso_animal} kg\n")
                archivo.write(f"Proteina de la mezcla    : {mezcla['proteina']:.2f}%\n")
                archivo.write(f"Energia de la mezcla     : {mezcla['energia']:.2f} Mcal\n")
                archivo.write(f"Fibra (FDN)              : {mezcla['fibra']:.2f}%\n")
                archivo.write(f"Ganancia Proyectada      : {ganancia:.3f} kg/dia\n")
                archivo.write(f"Costo por Kg Producido   : ${costo_por_kilo_producido:.2f}\n")
                archivo.write("=========================================\n")
            print("[+] Reporte 'Reporte_Lote.txt' guardado exitosamente en su carpeta.")
        except Exception as e:
            print(f"[!] Error al guardar el reporte: {e}")
#Sabrina regresaaaaaaa :'(
def iniciar_sistema():
    arsenal_vivo = cargar_memoria()
    ultimo_perfil = None
    ultima_mezcla = None

    while True:
        print("\n" + "="*45)
        print(" SISTEMA DE INTELIGENCIA AGROPECUARIA v2.0")
        print("="*45)
        print("[1] Consultar Arsenal Quimico")
        print("[2] Actualizar Precios de Mercado")
        print("[3] Diseñar Dieta") 
        print("[4] Laboratorio de Mezlcas") 
        print("[5] Piloto Automatico (Dietas Recomendadas)")
        print("[6] PRO: Gancia de Peso")
        print("[7] Apagar Sistema")
        print("="*45)

        orden = input("Seleccione una orden (1-7): ").strip()

        if orden == "1":
            consultar_inventario(arsenal_vivo)
        elif orden == "2": 
            actualizar_precio(arsenal_vivo)
        elif orden == "3": 
            ultimo_perfil = diseñar_dieta()
        elif orden == "4": 
            ultima_mezcla = auditar_mezcla(arsenal_vivo)
        elif orden == "5":
            recomendar_dieta_automatica(arsenal_vivo)
        elif orden == "6":
            if ultimo_perfil is None:
                print("\n[!] Error: No has diseñado el perfil del animal (Opcion 3).")
            elif ultima_mezcla is None:
                print("\n[!] Error: No has auditado una mezcla en el laboratorio (Opcion 4). ")
            else:
                calcular_ganancia_pro(ultimo_perfil, ultima_mezcla)
        elif orden == "7":
            print("\nApagando motores...")
            break
        else:
            print("\nERROR: Orden no reconocida. Intente de nuevo.")

iniciar_sistema()
 