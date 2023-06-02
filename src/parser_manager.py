# import pandas as pd
import json
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
from typing import Any


def parser_divs(content, class_: str) -> list[Tag]:
    soup = BeautifulSoup(content, 'html.parser')
    divs = soup.find_all(class_=class_)
    return divs
