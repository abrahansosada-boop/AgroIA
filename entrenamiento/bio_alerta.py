cultivo = input("Organismo: ")
poblacion = float(input("Poblacion actual: "))
if poblacion > 50:
    print(f"ALERTA: {cultivo} fuera de control.")
else:
    print(f"Estado: {cultivo} bajo control.")