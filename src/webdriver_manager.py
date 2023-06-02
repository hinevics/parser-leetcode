# Module for working with the webdriver
from typing import Any

from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logger
from myconfig import EXECUTABLE_PATH


def get_driver_page_source(url, driver, css_selector) -> tuple[Any, Any]:
    max_attempts = 2
    current_attempt = 1
    while current_attempt <= max_attempts:
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 15)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
            return driver.page_source, driver
        except TimeoutException as e:
            logger.logger.error(e)
            current_attempt += 1
    return None, driver


def get_driver() -> webdriver.Firefox:
    options = FirefoxOptions()
    options.add_argument('--headless')
    firefox_service = Service(EXECUTABLE_PATH)
    driver = webdriver.Firefox(
        service=firefox_service,
        options=options
    )
    return driver
