muestras = ["E.coli", "Salmonella", "Listeria"]
print(f"Primera muestra: {muestras[0]}")
nueva = input("nombre de nueva bacteria: ")
muestras.append(nueva)
print(f"Lista completa: {muestras}") 
print(f"Total de muestras: {len(muestras)}")