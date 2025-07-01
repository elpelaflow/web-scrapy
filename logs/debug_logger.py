import logging
import os

LOG_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(LOG_DIR, 'debug.log')
ERROR_FILE = os.path.join(LOG_DIR, 'errores.log')
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger('webscrapy')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    error_handler = logging.FileHandler(ERROR_FILE, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)