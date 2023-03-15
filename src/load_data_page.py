import pandas as pd
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from urllib.parse import urlencode, urlsplit, urlunsplit
import time
import logging
import json
import threading
import concurrent.futures

from config import (
    EXECUTABLE_PATH,
    PATH_PAGES,
    URL,
    ALG_URL,
)

MAX_PAGE = 24
MIN_PAGE = 23
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


def save_data(df, path):
    with open(path, 'w') as f:
        json.dump(df, f)


def loader_page(chunks):
    driver = starting_driver(EXECUTABLE_PATH)
    for page in chunks:
        logger.info(f'\033[31mSTART\033[0m\tparsing page: {page}')
        res_data = []
        url = create_url_wit_page(ALG_URL, page)
        driver.get(url)
        logger.info('\033[31mSTART\033[0m\tsleep')
        time.sleep(10)
        logger.info('\033[32mEND\033[0m\tsleep')
        content = driver.page_source
        alg_data = {}
        for div in parser_divs(content, class_=HTML_CLASS):  # возвращается список алгоритмов
            alg_data['number_page'] = page

            # alg_url
            alg_url = URL + div.find('a')['href']
            alg_data['url_alg'] = alg_url

            # alg_name
            text = div.find('a').text
            find = re.findall(pattern=REG_NAME_ALG, string=text)
            alg_name = ' '.join(re.findall(pattern=REG_NAME_ALG, string=text))
            alg_data['alg_name'] = alg_name

            # # difficult
            # difficult = div.find(class_='mx-2 py-[11px]')  # поиск сложности по классу
            # alg_data['difficult'] = difficult.text

            # alg_number
            search = re.search(pattern=REG_NUMBER_ALG, string=text)
            if search:
                alg_number = search.group()
            else:
                alg_number = None
            alg_data['alg_number'] = alg_number

            logger.info(f'\033[31mSTART\033[0m\tparsing alg {alg_number}.{alg_name}')
            driver.get(alg_url)
            time.sleep(5)
            alg_content = driver.page_source

            # descriptions
            alg_divs = parser_divs(alg_content, "_1l1MA")  # парсинг описания алгоритма, задачи
            if len(alg_divs) == 1:
                alg_data['descriptions'] = alg_divs[0].text
            logger.info(f'\033[31mSTART\033[0m\tparsing solutions for alg: {alg_number}')

            url_sol_alg = alg_url + 'solutions/' + '?orderBy=most_votes&page={page}'.format(
                page=1)  # пока только первая страница с решениями

            driver.get(url_sol_alg)
            time.sleep(5)
            sol_content = driver.page_source
            sol_names = parser_divs(
                sol_content,
                class_='truncate text-label-1 dark:text-dark-label-1 hover:text-blue-s dark:hover:'
                       'text-dark-blue-s text-[16px] font-medium leading-[22px]')
            sol_urls = parser_divs(
                sol_content,
                class_='no-underline hover:'
                       'text-blue-s dark:hover:text-dark-blue-s truncate w-full')
            sol_data = {}
            alg_data['solutions'] = []
            if len(sol_names) == len(sol_urls):
                for name, url in zip(sol_names, sol_urls):
                    sol_data['sol_name'] = name.text
                    sol_data['sol_url'] = url['href']
                    url_sol_for_alg = URL + url['href']

                    logger.info(f"\033[31mSTART\033[0m\tloading sol for {alg_number}:{sol_data['sol_name']}")
                    driver.get(url_sol_for_alg)
                    time.sleep(5)
                    sol = parser_divs(driver.page_source, class_='_16yfq _2YoR3')
                    if len(sol) == 1:
                        sol_data['sol'] = sol[0].text
                    alg_data['solutions'].append(sol_data)
                    logger.info(f"\033[32mEND\033[0m\tloading sol:{sol_data['sol_name']}")
                    sol_data = {}

            else:
                print('Error #1 ')
                break
            logger.info(f'\033[32mEND\033[0m\tparsing solutions\033[0m')
            logger.info(f'\033[32mEND\033[0m\tparsing alg {alg_number}.{alg_name}')

            res_data.append(alg_data)
            alg_data = {}
        save_path = PATH_PAGES + f'_{page}'
        save_data(df=res_data, path=save_path)
        logger.info(f'\033[32mEND\033[0m\tparsing page {page}')
        time.sleep(10)
        print('---' * 10)


def main():
    page_list = list(range(MIN_PAGE, MAX_PAGE))
    chunk_size = len(page_list) // 4
    chunks = [page_list[i:i+chunk_size] for i in range(0, len(page_list), chunk_size)]
    # Создаем новый поток и запускаем функцию loader_page в нем
    thread = threading.Thread(target=loader_page)
    thread.start()


    # Создаем пул потоков из нескольких воркеров
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Вызываем функцию load_page для каждого элемента списка параллельно
        futures = [executor.submit(loader_page, item) for item in chunks]

        # Ждем выполнения всех задач
        for future in concurrent.futures.as_completed(futures):
            result = future.result()

if __name__ == "__main__":
    main()
