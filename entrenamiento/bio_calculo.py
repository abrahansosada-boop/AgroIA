print("--- SISTEMA DE CALCULO BIO-ESTADISTICO ---")

nombre_bacteria = "E. coli"
tasa_crecimiento = 2 
horas = 5

poblacion_final = tasa_crecimiento ** horas 

print(f"Organismo: {nombre_bacteria}")
print(f"Tiempo transcurrido: {horas} horas")
print(f"Población estimada: {poblacion_final} unidades")
print("------------------------------------------")