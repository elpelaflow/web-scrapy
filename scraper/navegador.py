from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def crear_driver(headless: bool = True, proxy: str | None = None, user_agent: str | None = None) -> webdriver.Chrome:
    """Configura y devuelve una instancia de Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    if user_agent:
        options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver
    