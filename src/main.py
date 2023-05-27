# import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from urllib.parse import urlencode, urlsplit, urlunsplit
import tqdm
import time
import logging

from myconfig import (EXECUTABLE_PATH, MAX_PAGE,
                      MIN_PAGE, ALG_URL, HTML_FIELD_CLASS_ALGORITHM)


def color_log_green(text):
    return f'\033[31m{text}\033[0m'


def color_log_red(text):
    return f'\033[31m{text}\033[0m'


logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def get_driver():
    options = FirefoxOptions()
    options.add_argument('--headless')
    firefox_service = Service(EXECUTABLE_PATH)
    driver = webdriver.Firefox(
        service=firefox_service,
        options=options
    )
    return driver


def create_url_wit_page(url_: str, page_: int):
    url_parts = list(urlsplit(url_))
    query = dict(urlsplit(url_).query)
    query['page'] = f'{page_}'
    url_parts[3] = urlencode(query)
    new_url = urlunsplit(url_parts)
    return new_url


def parser_divs(content, class_):
    soup = BeautifulSoup(content, 'html.parser')
    divs = soup.find_all(class_=class_)
    return divs


def main():
    logger.info('Connecting to the driver')
    driver = get_driver()
    for n_page in tqdm.tqdm(MIN_PAGE, MAX_PAGE + 1):
        logger.info(f'Load page: {n_page}')
        url_page = create_url_wit_page(url_=ALG_URL, page_=n_page)
        driver.get(url_page)
        content_page = driver.page_source
        time.sleep(3)
        logger.info(color_log_green(f'Completed Loda page {n_page}'))
        algs_divs = parser_divs(content_page, class_=HTML_FIELD_CLASS_ALGORITHM)
        for j in tqdm.tqdm(range(5)):
            time.sleep(5)
        break


if __name__ == "__main__":
    main()
