# Module for collecting solutions of the algorithm
import pathlib
from urllib.parse import urlparse, urljoin
import aiohttp
import asyncio
from typing import Any

from get_algs import get_alg_url
import parser_manager
import webdriver_manager
import logger
from myconfig import (
    DATA_PAGE_ALGS_PATH,
    CSS_SELECTOR_ONE_ALG_PAGE
)

headers = {
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
}

query_totalNum = """query tabsStatus($titleSlug: String!) {
        questionTopicsList(questionSlug: $titleSlug) {totalNum}
        questionDiscussionTopic(questionSlug: $titleSlug) {topLevelCommentCount}}"""

DATA_PAGE_ALGS_PATH = pathlib.Path(DATA_PAGE_ALGS_PATH)


async def get_graphql_data(session: aiohttp.ClientSession, url: str, data: dict[str, Any]) -> dict[str, Any]:
    async with session.post(url, json=data) as respons:
        return await respons.json()


async def main():
    for alg in get_alg_url(directory_path=DATA_PAGE_ALGS_PATH):
        path = urlparse(alg['url']).path
        name_alg = path.strip('/').split('/')[-1]
        url = 'https://leetcode.com/graphql/'
        post_data_totalNum = {
            'query': query_totalNum,
            'variables': {"titleSlug": name_alg},
            'operationName': "tabsStatus"
        }
        async with aiohttp.ClientSession() as session:
            response = await get_graphql_data(session=session, url=url, data=post_data_totalNum)
            totalNum = response['data']['questionTopicsList']['totalNum']



if __name__ == "__main__":
    asyncio.run(main())
