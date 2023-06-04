# Module for collecting solutions of the algorithm
import pathlib

from get_algs import get_alg_url
import webdriver_manager
import logger
from myconfig import (
    DATA_PAGE_ALGS_PATH,
    CSS_SELECTOR_ONE_ALG_PAGE
)

DATA_PAGE_ALGS_PATH = pathlib.Path(DATA_PAGE_ALGS_PATH)


def main():
    for alg in get_alg_url(directory_path=DATA_PAGE_ALGS_PATH):

        driver = webdriver_manager.get_driver()

        content_alg, driver = webdriver_manager.get_driver_page_source(
            url=alg['url'],
            driver=driver, css_selector=CSS_SELECTOR_ONE_ALG_PAGE)

        if not content_alg:
            logger.logger.error(
                f"Error when loading alg {alg['name']}. Continue task wiht new alg."
            )
            continue

        logger.logger.info(f"Load desc of {alg['name']}")


if __name__ == "__main__":
    for i in get_alg_url(DATA_PAGE_ALGS_PATH):
        print(i)
