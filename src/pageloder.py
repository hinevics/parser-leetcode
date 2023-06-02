# import pandas as pd
import json
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
from urllib.parse import urlencode, urlsplit, urlunsplit, urljoin
import logging
from typing import Any

from myconfig import (
    EXECUTABLE_PATH, MAX_PAGE,
    MIN_PAGE, ALG_URL, URL,
    HTML_FIELD_CLASS_ALGORITHM,
    HTML_FIELD_CLASS_DECS_ALG,
    HTML_CLASS_SOLS,
    HTML_CLASS_PAGE,
    PATH_DATA)

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def color_log_green(text):
    return f'\033[32m{text}\033[0m'


def color_log_red(text):
    return f'\033[31m{text}\033[0m'


def load_page(url, driver, css_selector) -> tuple[Any, Any]:
    max_attempts = 2
    current_attempt = 1
    while current_attempt <= max_attempts:
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 15)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
            return driver.page_source, driver
        except TimeoutException as e:
            logger.error(color_log_red(f"Error: {e}"))
            current_attempt += 1
    return None


def get_driver():
    options = FirefoxOptions()
    options.add_argument('--headless')
    firefox_service = Service(EXECUTABLE_PATH)
    driver = webdriver.Firefox(
        service=firefox_service,
        options=options
    )
    return driver


def main():
    logger.info('Connecting to the driver')
    driver = get_driver()
    type(load_page())