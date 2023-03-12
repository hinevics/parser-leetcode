import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from urllib.parse import urlencode, urlsplit, urlunsplit
import time
import logging
import pickle
from tqdm import tqdm
from config import (
    EXECUTABLE_PATH,
    PATH_PAGES,
    URL,
    ALG_URL,
)

MAX_PAGE = 24
MIN_PAGE = 1
REG_NUMBER_ALG = r'\d+(?=\.)'
REG_NAME_ALG = r'[a-zA-Z]+'
HTML_CLASS = r'odd:bg-layer-1 even:bg-overlay-1 dark:odd:bg-dark-layer-bg dark:even:bg-dark-fill-4'

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


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


def starting_driver(executable):
    options = FirefoxOptions()
    options.add_argument('--headless')
    firefox_service = Service(executable)
    driver = webdriver.Firefox(
        service=firefox_service,
        options=options
    )
    return driver


def loader_page(driver):
    res_data = dict(url=[], page=[], alg_name=[], alg_number=[], html_page=[])
    for page in range(MIN_PAGE, MIN_PAGE + 1):
        if page > 2:
            break
        url = create_url_wit_page(ALG_URL, page)
        driver.get(url)
        logger.info('start sleep')
        time.sleep(10)
        logger.info('end sleep')
        content = driver.page_source
        logger.info(f'start parsing page{page}')
        for div in tqdm(parser_divs(content, class_=HTML_CLASS)):
            res_data['page'].append(page)

            # alg_url
            alg_url = URL + div.find('a')['href']
            res_data['url'].append(alg_url)

            # alg_name
            text = div.find('a').text
            find = re.findall(pattern=REG_NAME_ALG, string=text)
            alg_name = ' '.join(re.findall(pattern=REG_NAME_ALG, string=text))
            res_data['alg_name'].append(alg_name)

            # alg_number
            search = re.search(pattern=REG_NUMBER_ALG, string=text)
            if search:
                alg_number = search.group()
            else:
                alg_number = None
            res_data['alg_number'].append(alg_number)

            driver.get(alg_url)
            time.sleep(3)
            alg_content = driver.page_source
            res_data['html_page'].append(alg_content)
        logger.info(f'end parsing page{page}')
    df = pd.DataFrame(res_data)
    return df


def main():
    driver = starting_driver(EXECUTABLE_PATH)
    df = loader_page(driver)
    with open(PATH_PAGES, 'wb') as f:
        pickle.dump(df, f)


if __name__ == "__main__":
    main()
