from pathlib import Path

from .navegador import crear_driver
from .recolector import recolectar_negocios
from export.exportador import detectar_formato_y_exportar


def ejecutar_scraper(parametros: dict) -> tuple[str, int]:
    """Ejecuta todo el flujo de scraping y exportación."""
    pais = parametros.get("pais")
    provincia = parametros.get("provincia", "")
    localidad = parametros.get("localidad", "")
    categoria = parametros.get("categoria")
    palabra = parametros.get("palabra")
    limite = int(parametros.get("limite", 100))

    formato = parametros.get("formato", "csv")
    ruta = parametros.get(
        "ruta_salida",
        f"data/resultados/{categoria}_{palabra}_{localidad or provincia or pais}.{formato}",
    )
    ruta = ruta.replace(" ", "_")

    driver = crear_driver(headless=True)
    try:
        data = recolectar_negocios(
            driver, pais, provincia, localidad, categoria, palabra, limite
        )
    finally:
        driver.quit()

    detectar_formato_y_exportar(data, ruta)

    return ruta, len(data)
    