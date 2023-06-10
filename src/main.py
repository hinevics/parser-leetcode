# import pandas as pd
import json
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlencode, urlsplit, urlunsplit, urljoin
import logger
from typing import Any

from myconfig import (
    EXECUTABLE_PATH, MAX_PAGE,
    MIN_PAGE, ALG_URL, URL,
    HTML_FIELD_CLASS_ALGORITHM,
    HTML_FIELD_CLASS_DECS_ALG,
    HTML_CLASS_SOLS,
    HTML_CLASS_PAGE,
    PATH_DATA)

CSS_SELECTOR_ALGS_PAGE = (r"div.odd\:bg-layer-1:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) >"
                          r"div:nth-child(1) > div:nth-child(1) > a:nth-child(1)")
CSS_SELECTOR_ONE_ALG_PAGE = r'._1l1MA'
CSS_SELECTOR_SOLUTIONS = r'div.py-4:nth-child(1) > div:nth-child(1) > div:nth-child(1)'
CSS_SELECTOR_ONE_SOL = r'.break-words'


def color_log_green(text):
    return f'\033[32m{text}\033[0m'


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


def load_page(url, driver, css_selector):
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


def get_sol(divs_sols: list[Tag], driver):
    SOLUTIONS = []
    for sol in divs_sols:
        SOL = dict()
        SOL['name'] = sol.text
        SOL['url'] = urljoin(URL, divs_sols[0].a['href'])
        logger.info(f"Loading sol solutions {SOL['name']}")
        content_sol_page, driver = load_page(driver=driver, url=SOL['url'], css_selector=CSS_SELECTOR_ONE_SOL)
        if content_sol_page is None:
            logger.error(color_log_red(
                f"Error: Loading solution {SOL['name']}. Continue task wiht next sol")
            )
            continue
        logger.info(
            color_log_green(
                f"Completed load solution {SOL['name']}"
            )
        )
        div_sol_page = parser_divs(content_sol_page, class_='break-words')
        SOL['solution'] = div_sol_page[0].text
        divs_code_sol = parser_divs(content_sol_page, class_="px-3 py-2.5 bg-fill-3 dark:bg-dark-fill-3")
        SOL['code'] = divs_code_sol[0].text if divs_code_sol else ''
        divs_tag = parser_divs(
            content=content_sol_page,
            class_=HTML_CLASS_PAGE)
        SOL['tags'] = list({t.text for t in divs_tag[0].find_all('div')}) if divs_tag else []
        SOLUTIONS.append(SOL)
    return SOLUTIONS


def saver_alg(alg: dict[str, Any]):
    logger.info(f"ALG={alg['name']}. Start save alg.")
    with open(PATH_DATA.format(alg_name=alg['name']), "w") as file:
        json.dump(alg, file)
    logger.info(color_log_green(f"Completed load all solutions for {alg['name']}"))


def get_algs(algs_divs: list[Tag], driver):
    for alg in algs_divs:
        ALG = dict()
        text = alg.find('a').text
        ALG['name'] = ' '.join(re.findall(pattern=r'[a-zA-Z]+', string=text))
        ALG['url'] = urljoin(URL, alg.find('a')['href'])
        logger.info(f"ALG={ALG['name']}. Loading alg.")
        content_alg, driver = load_page(url=ALG['url'], driver=driver, css_selector=CSS_SELECTOR_ONE_ALG_PAGE)
        if content_alg is None:
            logger.error(color_log_red(
                f"Error:ALG={ALG['name']}. Loading alg. Continue task wiht next alg")
            )
            continue
        logger.info(color_log_green(
            f"ALG={ALG['name']}. Completed load alg.")
        )
        ALG['description'] = parser_divs(content=content_alg, class_=HTML_FIELD_CLASS_DECS_ALG)[0].text
        url_sols_alg = urljoin(ALG['url'], 'solutions/')
        logger.info(
            f"ALG={ALG['name']}. Loading alg solutions for {ALG['name']}"
        )
        content_sols, driver = load_page(driver=driver, url=url_sols_alg, css_selector=CSS_SELECTOR_SOLUTIONS)
        if content_sols is None:
            logger.error(color_log_red(
                f"Error: ALG={ALG['name']}. \
                    Loading solutions for alg {ALG['name']}. Continue task wiht next alg")
            )
            continue
        logger.info(color_log_green(
            f"ALG={ALG['name']}. Completed load solutions for alg {ALG['name']}"))
        divs_sols: list[Tag] = parser_divs(content_sols, HTML_CLASS_SOLS)
        ALG['sol'] = get_sol(divs_sols, driver)
        saver_alg(alg=ALG)


def main():
    logger.info('Connecting to the driver')
    driver = get_driver()
    for n_page in range(MIN_PAGE, MAX_PAGE + 1):
        url_page = create_url_wit_page(url_=ALG_URL, page_=n_page)
        logger.info(f'Loading page {n_page}')
        content_page, driver = load_page(url=url_page, driver=driver, css_selector=CSS_SELECTOR_ALGS_PAGE)
        if content_page is None:
            logger.error(
                color_log_red(
                    f'Error: PAGE={n_page}. Error when loading page. Continue task wiht new page.'
                )
            )
            continue
        logger.info(color_log_green(f'PAGE={n_page}. Completed loda page.'))
        algs_divs: list[Tag] = parser_divs(content_page, class_=HTML_FIELD_CLASS_ALGORITHM)
        get_algs(algs_divs, driver)
        logger.info(color_log_green(f"PAGE={n_page}. Completed loading page"))
    logger.info(color_log_green("Completed parsing data!"))


if __name__ == "__main__":
    main()
