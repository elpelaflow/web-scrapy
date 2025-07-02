import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logs.debug_logger import logger

from .extractor import extraer_ficha
from .utils import backoff_retry


@backoff_retry
def _navegar(driver, url: str) -> None:
    driver.get(url)
    try:
        consent = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[aria-label="Aceptar todo"]')
            )
        )
        consent.click()
        time.sleep(1)
    except Exception:
        pass


def recolectar_negocios(
    driver,
    pais: str,
    provincia: str,
    localidad: str,
    categoria: str,
    palabra_clave: str,
    limite: int = 100,
    timeout: int = 10,
    callback=None,
) -> list[dict]:
    """Navega por Google Maps y devuelve una lista de negocios.

    Parameters
    ----------
    timeout : int
        Segundos de espera para operaciones de Selenium.
    callback : callable | None
        Función llamada al completar cada ficha. Recibe el item,
        la cantidad recolectada y el límite establecido.
    """
    ubicacion = localidad or provincia or pais
    termino_busqueda = f"{categoria} {palabra_clave} en {ubicacion}"

    _navegar(driver, "https://www.google.com/maps")
    wait = WebDriverWait(driver, timeout)
    time.sleep(3)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(termino_busqueda)
    search_box.send_keys(Keys.ENTER)
    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pane [role='feed']"))
        )
    except Exception:
        pass
    time.sleep(2)

    # Realizar scroll dinámico hasta alcanzar el límite o no haya más resultados
    scrollable_div = None
    try:
        scrollable_div = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pane [role='feed']"))
        )
    except Exception:
        logger.error(
            "No se encontró el contenedor de resultados en Maps", exc_info=True
        )
        return []

    results: list = scrollable_div.find_elements(
        By.CSS_SELECTOR, "a[href*='/place/']"
    )
    prev_count = len(results)

    while len(results) < limite:
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight",
            scrollable_div,
        )
        time.sleep(2)
        results = scrollable_div.find_elements(By.CSS_SELECTOR, "a[href*='/place/']")
        new_count = len(results)
        logger.info("Encontrados %d negocios tras scroll", new_count)
        if new_count == prev_count:
            break
        prev_count = new_count
        if new_count >= limite:
            break

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
            if callback:
                callback(item, len(data), limite)
            driver.back()
            time.sleep(2)
        except Exception:
            continue

    return data
    