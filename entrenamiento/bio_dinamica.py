print("--- CALCULADORA VETTEL ---")

cultivo = input("Nombre del microorganismo: ")
horas = float(input("Horas de incubación: "))

poblacion = 2 ** horas

print(f"Resultado para {cultivo}:")
print(f"Población final: {poblacion}")