import os
from dotenv import load_dotenv

load_dotenv()

ALG_URL = r'https://leetcode.com/problemset/algorithms'
URL = r'https://leetcode.com'
MAX_PAGE = 24
MIN_PAGE = 1
REG_NUMBER_ALG = r'\d+(?=\.)'
EXECUTABLE_PATH = os.getenv("EXECUTABLE_PATH")

# HTML CLASS
HTML_FIELD_CLASS_ALGORITHM = r'odd:bg-layer-1 even:bg-overlay-1 dark:odd:bg-dark-layer-bg dark:even:bg-dark-fill-4'
HTML_FIELD_CLASS_DECS_ALG = r'_1l1MA'
HTML_CLASS_SOLS = r'flex min-w-0 max-w-full items-center gap-2'
HTML_CLASS_PAGE = r'flex flex-grow flex-nowrap items-center gap-2 overflow-hidden my-1'
