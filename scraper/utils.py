import time
from functools import wraps
from selenium.common.exceptions import TimeoutException, WebDriverException


def backoff_retry(func):
    """Retry a function with exponential backoff when Selenium timeouts occur."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except (TimeoutException, WebDriverException):
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    return wrapper