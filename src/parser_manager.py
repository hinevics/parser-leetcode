from bs4 import BeautifulSoup
from bs4.element import Tag


def parser_divs(content, class_: str) -> list[Tag]:
    soup = BeautifulSoup(content, 'html.parser')
    divs = soup.find_all(class_=class_)
    return divs
