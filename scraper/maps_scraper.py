# maps_scraper.py

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import re
import requests

def buscar_negocios(pais, provincia, localidad, categoria, palabra_clave, limite=100):
    ubicacion = localidad or provincia or pais
    termino_busqueda = f"{categoria} {palabra_clave} en {ubicacion}"

    print(f"[INFO] Buscando: {termino_busqueda}")

    # Inicializar Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.google.com/maps")
    time.sleep(3)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(termino_busqueda)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.m6QErb")
    for _ in range(3):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(3)

    results = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
    data = []

    for result in results[:limite]:
        try:
            result.find_element(By.CSS_SELECTOR, "a").click()
            time.sleep(3)

            name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf" ).text
            try:
                address = driver.find_element(By.CSS_SELECTOR, "div[data-item-id='address'] span" ).text
            except:
                address = ""

            try:
                phone = driver.find_element(By.CSS_SELECTOR, "div[data-tooltip='Copiar el número de teléfono'] span" ).text
            except:
                phone = ""

            try:
                website = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']").get_attribute("href")
            except:
                website = ""

            # Buscar email en sitio web (si existe)
            email = ""
            if website:
                try:
                    response = requests.get(website, timeout=5)
                    soup = BeautifulSoup(response.text, "html.parser")
                    emails = re.findall(r"[\w\.-]+@[\w\.-]+", soup.get_text())
                    email = emails[0] if emails else ""
                except:
                    pass

            data.append({
                "Name": name,
                "Phone Number": phone,
                "Email": email,
                "Address": address,
                "Province": provincia,
                "City": localidad,
                "Country": pais,
                "Category": categoria,
                "Keyword": palabra_clave,
                "Web Domain": website
            })

            driver.back()
            time.sleep(2)
        except:
            continue

    driver.quit()

    # Guardar CSV
    os.makedirs("data/resultados", exist_ok=True)
    filename = f"data/resultados/{categoria}_{palabra_clave}_{ubicacion}.csv".replace(" ", "_")
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

    print(f"[INFO] Guardado: {filename}")
    return filename, len(data)
