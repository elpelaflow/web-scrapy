import logging
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), 'debug.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logger = logging.getLogger('webscrapy')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)