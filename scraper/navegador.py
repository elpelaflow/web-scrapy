from pathlib import Path
import itertools
import yaml
import undetected_chromedriver as uc

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def _load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def crear_driver(headless: bool | None = None, proxy: str | None = None, user_agent: str | None = None) -> uc.Chrome:
    """Devuelve una instancia de Chrome configurada con proxy y User-Agent rotativos."""
    config = _load_config()
    user_agent_pool = itertools.cycle(config.get("user_agents", []))
    proxy_pool = itertools.cycle(config.get("proxies", []))

    options = uc.ChromeOptions()
    headless_value = headless if headless is not None else config.get("headless", True)
    if headless_value:
        options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    if proxy is None and config.get("proxies"):
        proxy = next(proxy_pool)
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    if user_agent is None and config.get("user_agents"):
        user_agent = next(user_agent_pool)
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    return uc.Chrome(options=options)
    