import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .extractor import extraer_ficha


def recolectar_negocios(driver, pais: str, provincia: str, localidad: str,
                         categoria: str, palabra_clave: str, limite: int = 100) -> list[dict]:
    """Navega por Google Maps y devuelve una lista de negocios."""
    ubicacion = localidad or provincia or pais
    termino_busqueda = f"{categoria} {palabra_clave} en {ubicacion}"

    driver.get("https://www.google.com/maps")
    time.sleep(3)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(termino_busqueda)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    # Realizar scroll para cargar resultados
    try:
        scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.m6QErb")
        for _ in range(3):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div
            )
            time.sleep(3)
    except Exception:
        pass

    results = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
    data = []

    for result in results[:limite]:
        try:
            result.find_element(By.CSS_SELECTOR, "a").click()
            time.sleep(3)
            item = extraer_ficha(
                driver, provincia, localidad, categoria, palabra_clave, pais
            )
            data.append(item)
            driver.back()
            time.sleep(2)
        except Exception:
            continue

    return data