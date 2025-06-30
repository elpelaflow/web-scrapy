import logging
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), 'descargas_error.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.WARNING)

if not _logger.handlers:
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

def registrar_error(url: str, error: Exception):
    """Registra en el log un fallo de descarga."""
    _logger.warning("Fallo al descargar %s: %s", url, error)