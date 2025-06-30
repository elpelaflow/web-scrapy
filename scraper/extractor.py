from bs4 import BeautifulSoup
import re
import requests
from selenium.webdriver.common.by import By


def extraer_ficha(driver, provincia: str, localidad: str, categoria: str,
                   palabra_clave: str, pais: str) -> dict:
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
        try:
            response = requests.get(website, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            emails = re.findall(r"[\w\.-]+@[\w\.-]+", soup.get_text())
            email = emails[0] if emails else ""
        except Exception:
            pass

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
    