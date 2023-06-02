from urllib.parse import urlencode, urlsplit, urlunsplit


def create_url_wit_page(url_: str, page_: int):
    url_parts = list(urlsplit(url_))
    query = dict(urlsplit(url_).query)
    query['page'] = f'{page_}'
    url_parts[3] = urlencode(query)
    new_url = urlunsplit(url_parts)
    return new_url
