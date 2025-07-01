from pathlib import Path
import yaml
from logs.debug_logger import logger

from .navegador import crear_driver
from .recolector import recolectar_negocios
from export.exportador import exportar

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def ejecutar_scraper(parametros: dict, callback=None) -> tuple[str, int]:
    """Ejecuta todo el flujo de scraping y exportación."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        pais = parametros.get("pais")
        provincia = parametros.get("provincia", "")
        localidad = parametros.get("localidad", "")
        categoria = parametros.get("categoria")
        palabra = parametros.get("palabra")
        limite = int(parametros.get("limite", config.get("limit", 100)))

        formato = parametros.get("formato", "csv")
        ruta = parametros.get("ruta_salida", "data/resultados")
        ruta = ruta.replace(" ", "_")

        headless = config.get("headless", True)

        logger.info(
            "Iniciando scraping: %s, %s, %s, %s, %s",
            pais,
            provincia,
            localidad,
            categoria,
            palabra,
        )
        driver = crear_driver(headless=headless)
        try:
            data = recolectar_negocios(
                driver,
                pais,
                provincia,
                localidad,
                categoria,
                palabra,
                limite,
                timeout=config.get("timeout", 10),
                callback=callback,
            )
        finally:
            driver.quit()

        archivo = exportar(data, formato, ruta)
        logger.info("Exportado a %s: %s", formato, archivo)

        return archivo, len(data)
    except Exception:
        logger.exception("Error en ejecutar_scraper")
        raise
    