from __future__ import annotations

from pathlib import Path
import yaml
import requests

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

GEOCODER = CONFIG.get("geocoder", "none").lower()


def geocode(address: str) -> tuple[float | None, float | None]:
    """Devuelve latitud y longitud de la dirección usando la API configurada."""
    if not address or GEOCODER == "none":
        return None, None

    try:
        if GEOCODER == "nominatim":
            params = {"q": address, "format": "json", "limit": 1}
            headers = {"User-Agent": "web-scrapy"}
            resp = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params=params,
                headers=headers,
                timeout=5,
            )
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        elif GEOCODER == "google":
            key = CONFIG.get("google_api_key")
            params = {"address": address}
            if key:
                params["key"] = key
            resp = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params=params,
                timeout=5,
            )
            result = resp.json().get("results")
            if result:
                location = result[0]["geometry"]["location"]
                return float(location["lat"]), float(location["lng"])
    except Exception:
        pass

    return None, None