
import json
from pathlib import Path

CAMPOS = [
    "id", "nombre", "lat", "lng", "popularidad",
    "sargazo", "temp_agua", "fragilidad",
    "transporte", "nota"
]

# Cargar archivo JSON
ruta = Path(__file__).parent / "playas.json"

try:
    playas = json.loads(ruta.read_text(encoding="utf-8"))
except FileNotFoundError:
    print(f"Error: no se encontró el archivo {ruta}")
    raise SystemExit(1)
except json.JSONDecodeError as e:
    print(f"Error: el JSON no es válido: {e}")
    raise SystemExit(1)

# Comprobar estructura general
if not isinstance(playas, list):
    print("Error: el archivo debe contener una lista de playas.")
    raise SystemExit(1)

errores = 0

for p in playas:
    if not isinstance(p, dict):
        print("Error: se encontró un elemento que no es un objeto JSON.")
        errores += 1
        continue

    nombre = p.get("id", "SIN ID")

    # Comprobar campos obligatorios
    faltan = [campo for campo in CAMPOS if campo not in p]

    if faltan:
        print(nombre, "-> faltan campos:", faltan)
        errores += 1
        continue

    # Popularidad: número entre 0 y 1
    popularidad = p["popularidad"]

    if (
        not isinstance(popularidad, (int, float))
        or isinstance(popularidad, bool)
        or not 0 <= popularidad <= 1
    ):
        print(nombre, "-> popularidad debe ser un número entre 0 y 1")
        errores += 1

    # Sargazo y fragilidad: número entre 0 y 100 o null
    for campo in ("sargazo", "fragilidad"):
        valor = p[campo]

        if valor is not None and (
            not isinstance(valor, (int, float))
            or isinstance(valor, bool)
            or not 0 <= valor <= 100
        ):
            print(nombre, "->", campo, "debe estar entre 0 y 100 o ser null")
            errores += 1

    # Temperatura del agua: número entre 20 y 35 °C
    temp = p["temp_agua"]

    if (
        not isinstance(temp, (int, float))
        or isinstance(temp, bool)
        or not 20 <= temp <= 35
    ):
        print(nombre, "-> temp_agua se ve rara:", temp)
        errores += 1

    # Coordenadas
    for campo, minimo, maximo in (
        ("lat", -90, 90),
        ("lng", -180, 180)
    ):
        valor = p[campo]

        if (
            not isinstance(valor, (int, float))
            or isinstance(valor, bool)
            or not minimo <= valor <= maximo
        ):
            print(nombre, "-> coordenada inválida:", campo, valor)
            errores += 1

    # Campos de texto
    for campo in ("id", "nombre", "transporte", "nota"):
        if not isinstance(p[campo], str):
            print(nombre, "->", campo, "debe ser texto")
            errores += 1

print("\nRevisadas:", len(playas), "playas")
print("Errores encontrados:", errores)

if errores == 0:
    print("Validación completada: todos los datos son correctos.")
else:
    print("Validación completada: revisa los errores anteriores.")
