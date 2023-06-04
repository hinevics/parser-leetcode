# module for assembling all links to algorithms
from typing import Any
import json
from bs4.element import Tag
import re
from urllib.parse import urljoin
import pathlib

from selenium import webdriver

import webdriver_manager
import url_manager
import logger
import parser_manager

from myconfig import (
    ALG_URL, MIN_PAGE, MAX_PAGE,
    CSS_SELECTOR_ALGS_PAGE, URL, HTML_FIELD_CLASS_ALGORITHM,
    DATA_PAGE_ALGS_PATH, CSS_SELECTOR_ONE_ALG_PAGE, HTML_FIELD_CLASS_DECS_ALG
)


DATA_PAGE_ALGS_PATH = pathlib.Path(DATA_PAGE_ALGS_PATH)


def get_desc(url: str, driver: webdriver.Firefox) -> str:
    # returns a description
    logger.logger.info(f'Start load description of {url}')

    content_alg, driver = webdriver_manager.get_driver_page_source(
            url=url,
            driver=driver, css_selector=CSS_SELECTOR_ONE_ALG_PAGE)

    if not content_alg:
        logger.logger.error(f'Error when loading page {url}. Return empty desc')
        return ''

    description = parser_manager.parser_divs(
        content=content_alg,
        class_=HTML_FIELD_CLASS_DECS_ALG
    )[0].text
    logger.logger.info(f'Done loading description of {url}')
    return description


def get_algs(algs_divs: list[Tag], driver: webdriver.Firefox) -> list[dict[str, str]]:
    # returns everything according to the algorithm
    ALGS = []
    for alg in algs_divs:
        ALG = dict()
        text = alg.find('a').text
        ALG['name'] = ' '.join(re.findall(pattern=r'[a-zA-Z]+', string=text))
        ALG['url'] = urljoin(URL, alg.find('a')['href'])
        ALG['description'] = get_desc(url=ALG['url'], driver=driver)
        ALGS.append(ALG)
    return ALGS


def check_path(path: pathlib.PosixPath) -> bool:
    if path.exists():
        return path
    logger.logger.warning(f'Dir in path ({path}) not exists.')
    path = path.mkdir(parents=True, exist_ok=True)
    logger.logger.info(f'Dir in path ({path}) created.')
    return path


def saver(page_algs: list[dict[str, Any]], path: pathlib.PosixPath, n_page: int):
    if path := check_path(path):
        path = path.joinpath(f'{n_page}').with_suffix('.json')
        with open(file=path, mode='w', encoding='utf-8') as file:
            json.dump(page_algs, file)


def main():
    logger.logger.info('CONNECTING TO THE DRIVER.')
    driver = webdriver_manager.get_driver()
    stoper_loding_page = 0
    logger.logger.info('START PARSING PAGES.')
    for n_page in range(MIN_PAGE, MAX_PAGE + 1):
        url_page = url_manager.create_url_wit_page(url_=ALG_URL, page_=n_page)
        logger.logger.info(f'Page {n_page} loading.')
        content_page, driver = webdriver_manager.get_driver_page_source(
            url=url_page,
            driver=driver, css_selector=CSS_SELECTOR_ALGS_PAGE)

        if not content_page:
            logger.logger.error(
                f'Error when loading page {n_page}. Continue task wiht new page.'
            )
            continue

        logger.logger.info('Search for divs.')
        algs_divs: list[Tag] = parser_manager.parser_divs(content_page, class_=HTML_FIELD_CLASS_ALGORITHM)
        algs = get_algs(algs_divs=algs_divs, driver=driver)

        logger.logger.info(f'Saving a page {n_page}.')
        if algs:
            saver(algs, path=DATA_PAGE_ALGS_PATH, n_page=n_page)
        else:
            if stoper_loding_page > 5:
                logger.logger.critical(
                    f'The parser returns empty pages. n_page={n_page}, \
                    stoper_loding_page={stoper_loding_page}')
                raise ValueError('The parser returns empty pages')
            logger.logger.error('Algs empty. Next page loding')
            stoper_loding_page += 1
            continue

        logger.logger.info(f'Page {n_page} loading completed.')
    logger.logger.info('Done load pages')


if __name__ == '__main__':
    main()
