import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .extractor import extraer_ficha
from .utils import backoff_retry


@backoff_retry
def _navegar(driver, url: str) -> None:
    driver.get(url)


def recolectar_negocios(
    driver,
    pais: str,
    provincia: str,
    localidad: str,
    categoria: str,
    palabra_clave: str,
    limite: int = 100,
    timeout: int = 10,
) -> list[dict]:
    """Navega por Google Maps y devuelve una lista de negocios.

    Parameters
    ----------
    timeout : int
        Segundos de espera para operaciones de Selenium.
    """
    ubicacion = localidad or provincia or pais
    termino_busqueda = f"{categoria} {palabra_clave} en {ubicacion}"

    _navegar(driver, "https://www.google.com/maps")
    wait = WebDriverWait(driver, timeout)
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

    # Realizar scroll dinámico hasta alcanzar el límite o no haya más resultados
    results: list = []
    try:
        scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.m6QErb")
        results = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
        if not results:
            results = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
        prev_count = len(results)

        while len(results) < limite:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                scrollable_div,
            )
            try:
                wait.until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "div[role='article']")) > prev_count
                )
            except Exception:
                break
            results = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            if not results:
                results = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
            if len(results) == prev_count:
                break
            prev_count = len(results)
    except Exception:
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
    