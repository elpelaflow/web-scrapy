from pathlib import Path
import random
import yaml

from .navegador import crear_driver
from .recolector import recolectar_negocios
from export.exportador import detectar_formato_y_exportar

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)


def ejecutar_scraper(parametros: dict) -> tuple[str, int]:
    """Ejecuta todo el flujo de scraping y exportación."""
    pais = parametros.get("pais")
    provincia = parametros.get("provincia", "")
    localidad = parametros.get("localidad", "")
    categoria = parametros.get("categoria")
    palabra = parametros.get("palabra")
    limite = int(parametros.get("limite", CONFIG.get("limit", 100)))

    formato = parametros.get("formato", "csv")
    ruta = parametros.get(
        "ruta_salida",
        f"data/resultados/{categoria}_{palabra}_{localidad or provincia or pais}.{formato}",
    )
    ruta = ruta.replace(" ", "_")

    user_agents = CONFIG.get("user_agents") or []
    proxies = CONFIG.get("proxies") or []
    user_agent = random.choice(user_agents) if user_agents else None
    proxy = random.choice(proxies) if proxies else None
    headless = CONFIG.get("headless", True)

    driver = crear_driver(headless=headless, proxy=proxy, user_agent=user_agent)
    try:
        data = recolectar_negocios(
            driver,
            pais,
            provincia,
            localidad,
            categoria,
            palabra,
            limite,
            timeout=CONFIG.get("timeout", 10),
        )
    finally:
        driver.quit()

    detectar_formato_y_exportar(data, ruta)

    return ruta, len(data)
    