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
