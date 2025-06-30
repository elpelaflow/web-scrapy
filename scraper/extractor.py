from bs4 import BeautifulSoup
import re
import requests
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from logs.descargas_log import registrar_error


def _obtener_user_agent(custom_ua: str | None = None) -> str:
    """Devuelve un User-Agent válido."""
    if custom_ua:
        return custom_ua
    try:
        return UserAgent().random
    except Exception:
        return (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )


def extraer_ficha(
    driver,
    provincia: str,
    localidad: str,
    categoria: str,
    palabra_clave: str,
    pais: str,
    user_agent: str | None = None,
) -> dict:
    """Extrae los datos de la ficha de un negocio abierto en el driver."""
    name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
    address = ""
    phone = ""
    website = ""

    try:
        address = driver.find_element(By.CSS_SELECTOR, "div[data-item-id='address'] span").text
    except Exception:
        pass

    try:
        phone = driver.find_element(By.CSS_SELECTOR, "div[data-tooltip='Copiar el número de teléfono'] span").text
    except Exception:
        pass

    try:
        website = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']").get_attribute("href")
    except Exception:
        pass

    email = ""
    if website:
        headers = {"User-Agent": _obtener_user_agent(user_agent)}
        try:
            response = requests.get(website, timeout=5, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            emails = re.findall(r"[\w\.-]+@[\w\.-]+", soup.get_text())
            email = emails[0] if emails else ""
        except requests.RequestException as e:
            registrar_error(website, e)

    return {
        "Name": name,
        "Phone Number": phone,
        "Email": email,
        "Address": address,
        "Province": provincia,
        "City": localidad,
        "Country": pais,
        "Category": categoria,
        "Keyword": palabra_clave,
        "Web Domain": website,
    }
    