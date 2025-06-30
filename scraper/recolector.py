import time
import math
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

    # Realizar scroll para cargar más resultados en la lista lateral
    try:
        scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.m6QErb")
        # Calculamos la cantidad de scrolls aproximados asumiendo que cada uno
        # carga alrededor de 10 nuevos negocios
        num_scrolls = math.ceil(limite / 10)
        for _ in range(num_scrolls):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                scrollable_div,
            )
            time.sleep(2)
    except Exception:
        # Si el contenedor no se encuentra continuamos sin lanzar error
        pass

    # Cada resultado suele estar en un contenedor con el rol "article"
    results = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
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
    