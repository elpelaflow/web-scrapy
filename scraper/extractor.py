from __future__ import annotations

import os
import re
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from logs.descargas_log import registrar_error
from .geocoder import geocode


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
    latitude = None
    longitude = None
    rating = None
    reviews_count = None
    hours = {}
    image_path = ""

    try:
        address = driver.find_element(By.CSS_SELECTOR, "div[data-item-id='address'] span").text
    except Exception:
        pass

    if address:
        latitude, longitude = geocode(address)

    try:
        phone = driver.find_element(By.CSS_SELECTOR, "div[data-tooltip='Copiar el número de teléfono'] span").text
    except Exception:
        pass

    try:
        website = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']").get_attribute("href")
    except Exception:
        pass

    try:
        rating_el = driver.find_element(By.CSS_SELECTOR, "span[aria-label$='estrellas']")
        rating_label = rating_el.get_attribute("aria-label")
        rating = float(rating_label.split()[0].replace(",", "."))
    except Exception:
        pass

    try:
        reviews_el = driver.find_element(By.CSS_SELECTOR, "span[aria-label$='reseñas']")
        match = re.search(r"(\d+[.,]?\d*)", reviews_el.get_attribute("aria-label") or reviews_el.text)
        if match:
            reviews_count = int(match.group(1).replace(".", "").replace(",", ""))
    except Exception:
        pass

    # Obtener horarios
    try:
        hours_btn = driver.find_element(By.CSS_SELECTOR, "button[jsaction*='pane.hours']")
        hours_btn.click()
    except Exception:
        pass

    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "table[aria-label] tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                day = cols[0].text.replace(":", "").strip()
                hours[day] = cols[1].text.strip()
    except Exception:
        pass

    # Descargar imagen principal
    try:
        img_el = driver.find_element(By.CSS_SELECTOR, "img[role='img']")
        img_url = img_el.get_attribute("src")
        if img_url:
            os.makedirs("images", exist_ok=True)
            filename = re.sub(r"\W+", "_", name.lower()) + ".jpg"
            filepath = os.path.join("images", filename)
            resp = requests.get(img_url, timeout=10)
            with open(filepath, "wb") as f:
                f.write(resp.content)
            image_path = filepath
    except Exception as e:
        if 'img_url' in locals():
            registrar_error(img_url, e)

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
        "Latitude": latitude,
        "Longitude": longitude,
        "Province": provincia,
        "City": localidad,
        "Country": pais,
        "Category": categoria,
        "Keyword": palabra_clave,
        "Web Domain": website,
        "Rating": rating,
        "Reviews": reviews_count,
        "Hours": hours,
        "Image Path": image_path,
    }
    