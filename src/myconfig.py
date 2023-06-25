import os
from dotenv import load_dotenv

load_dotenv()

ALG_URL = r'https://leetcode.com/problemset/algorithms'
URL = r'https://leetcode.com'
URL_API = r'https://leetcode.com/graphql/'
MAX_PAGE = 24
MIN_PAGE = 1
REG_NUMBER_ALG = r'\d+(?=\.)'
EXECUTABLE_PATH = os.getenv("EXECUTABLE_PATH")
LOG_PATH = os.getenv('LOG_PATH')
LOG_ERROR_PATH = os.getenv("LOG_ERROR_PATH")
DATA_ONE_ALG_PATH = os.getenv('DATA_ONE_ALG_PATH')
DATA_PAGE_ALGS_PATH = os.getenv('DATA_PAGE_ALGS_PATH')
PATH_DATA = os.getenv('PATH_DATA')

# HTML CLASS
HTML_FIELD_CLASS_ALGORITHM = r'odd:bg-layer-1 even:bg-overlay-1 dark:odd:bg-dark-layer-bg dark:even:bg-dark-fill-4'
HTML_FIELD_CLASS_DECS_ALG = r'_1l1MA'
HTML_CLASS_SOLS = r'flex min-w-0 max-w-full items-center gap-2'
HTML_CLASS_PAGE = r'flex flex-grow flex-nowrap items-center gap-2 overflow-hidden my-1'

# css selector
CSS_SELECTOR_ALGS_PAGE = (
    r"div.odd\:bg-layer-1:nth-child(2) > div:nth-child(2) >"
    r"div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)"
)
CSS_SELECTOR_ONE_ALG_PAGE = r'._1l1MA'
CSS_SELECTOR_SOLUTIONS = r'div.py-4:nth-child(1) > div:nth-child(1) > div:nth-child(1)'
CSS_SELECTOR_ONE_SOL = r'.break-words'
