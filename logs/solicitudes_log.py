import os
import csv
from datetime import datetime

def registrar_log(pais, provincia, localidad, categoria, palabra, limite, archivo, cantidad, runtime_seconds):
    os.makedirs("logs", exist_ok=True)
    archivo_log = "logs/solicitudes_log.csv"
    existe = os.path.isfile(archivo_log)

    with open(archivo_log, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow([
                "Fecha y Hora", "País", "Provincia", "Localidad",
                "Categoría", "Palabra Clave", "Límite",
                "Archivo CSV", "Cantidad de Resultados", "Runtime Seconds"
            ])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pais, provincia, localidad, categoria,
            palabra, limite, archivo, cantidad, f"{runtime_seconds:.2f}"
        ])
