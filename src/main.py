# import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from urllib.parse import urlencode, urlsplit, urlunsplit, urljoin
import tqdm
import time
import logging

from myconfig import (
    EXECUTABLE_PATH, MAX_PAGE,
    MIN_PAGE, ALG_URL, URL,
    HTML_FIELD_CLASS_ALGORITHM,
    HTML_FIELD_CLASS_DECS_ALG,
    HTML_CLASS_SOLS,
    HTML_CLASS_PAGE)

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def color_log_green(text):
    return f'\033[31m{text}\033[0m'


def color_log_red(text):
    return f'\033[31m{text}\033[0m'


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


def parser_divs(content, class_: str) -> list[Tag]:
    soup = BeautifulSoup(content, 'html.parser')
    divs = soup.find_all(class_=class_)
    return divs


def main():
    RES_DATA = []
    logger.info('Connecting to the driver')
    driver = get_driver()
    for n_page in tqdm.tqdm(range(MIN_PAGE, MAX_PAGE + 1)):
        logger.info(f'Load page: {n_page}')
        url_page = create_url_wit_page(url_=ALG_URL, page_=n_page)
        driver.get(url_page)
        content_page = driver.page_source
        time.sleep(10)
        logger.info(color_log_green(f'Completed Loda page {n_page}'))
        algs_divs: list[Tag] = parser_divs(content_page, class_=HTML_FIELD_CLASS_ALGORITHM)
        # TODO: вынести в отдельную функцию
        print(algs_divs[1])
        for alg in tqdm.tqdm(algs_divs):
            ALG = dict()
            text = alg.find('a').text
            ALG['name'] = ' '.join(re.findall(pattern=r'[a-zA-Z]+', string=text), string=text)
            ALG['url'] = urljoin(URL, alg.find('a')['href'])
            driver.get(ALG['url'])
            time.sleep(2)
            content_alg = driver.page_source
            desc = parser_divs(content=content_alg, class_=HTML_FIELD_CLASS_DECS_ALG)[0].text
            ALG['description'] = desc
            url_sols_alg = urljoin(ALG['url'], 'solutions/')
            # TODO: Вынести в отдельную функцию все driver get url wiht time sleep
            driver.get(url_sols_alg)
            time.sleep(2)
            content_sols = driver.page_source
            divs_sols: list[Tag] = parser_divs(content_sols, HTML_CLASS_SOLS) 
            SOLUTIONS = []
            for sol in tqdm.tqdm(divs_sols):
                SOL = dict()
                SOL['name'] = sol.text
                SOL['url'] = urljoin(URL, divs_sols[0].a['href'])
                driver.get(SOL['url'])
                time.sleep(2)
                content_sol_page = driver.page_source
                div_sol_page = parser_divs(content_sol_page, class_='break-words')
                SOL['solution'] = div_sol_page[0].text
                divs_code_sol = parser_divs(content_sol_page, class_='group relative')
                SOL['code'] = divs_code_sol[0].text
                divs_tag = parser_divs(
                    content=content_sol_page,
                    class_=HTML_CLASS_PAGE)
                SOL['tags'] = {t.text for t in divs_tag[0].find_all('div')}
                SOLUTIONS.append(SOL)
                break
        RES_DATA.append(ALG)
        break


if __name__ == "__main__":
    main()
