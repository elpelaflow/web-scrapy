import time
import math
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .extractor import extraer_ficha


def recolectar_negocios(driver, pais: str, provincia: str, localidad: str,
                         categoria: str, palabra_clave: str, limite: int = 100) -> list[dict]:
    """Navega por Google Maps y devuelve una lista de negocios."""
    ubicacion = localidad or provincia or pais
    termino_busqueda = f"{categoria} {palabra_clave} en {ubicacion}"

    driver.get("https://www.google.com/maps")
    wait = WebDriverWait(driver, 10)
    time.sleep(3)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(termino_busqueda)
    search_box.send_keys(Keys.ENTER)
    # Esperar a que aparezca la lista de resultados
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb")))
    except Exception:
        pass
    time.sleep(2)

    # Realizar scroll para cargar más resultados en la lista lateral
    try:
        scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.m6QErb")
        # Calculamos la cantidad de scrolls aproximados asumiendo que cada uno
        # carga alrededor de 10 nuevos negocios. Garantizamos al menos 3 ciclos
        num_scrolls = max(3, math.ceil(limite / 10))
        for _ in range(num_scrolls):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                scrollable_div,
            )
            # Esperar a que se carguen nuevos elementos tras cada scroll
            time.sleep(2)
    except Exception:
        # Si el contenedor no se encuentra continuamos sin lanzar error
        pass

    # Localizar los contenedores de cada negocio en la lista lateral
    results = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
    # Fallback por si la estructura cambia
    if not results:
        results = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
    if not results:
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='article']")))
            results = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
        except Exception:
            pass
    data = []

    for result in results[:limite]:
        try:
            link = result.find_element(By.CSS_SELECTOR, "a")
            driver.execute_script("arguments[0].click();", link)
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
    