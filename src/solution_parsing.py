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

query_tabsStatus = """query tabsStatus($titleSlug: String!) {
        questionTopicsList(questionSlug: $titleSlug) {totalNum}
        questionDiscussionTopic(questionSlug: $titleSlug) {topLevelCommentCount}}"""
query_communitySolutions = """query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $query: String, $orderBy: TopicSortingOption, $languageTags: [String!], $topicTags: [String!]) { questionSolutions(   filters: {questionSlug: $questionSlug, skip: $skip, first: $first, query: $query, orderBy: $orderBy, languageTags: $languageTags, topicTags: $topicTags} ) {   hasDirectResults   totalNum   solutions { id title commentCount topLevelCommentCount viewCount pinned isFavorite solutionTags {   name   slug } post {   id   status   voteCount   creationDate   isHidden   author {     username     isActive     nameColor     activeBadge {       displayName       icon     }     profile {       userAvatar       reputation     }   } } searchMeta {   content   contentType   commentAuthor { username } replyAuthor { username } highlights}}}}"""
DATA_PAGE_ALGS_PATH = pathlib.Path(DATA_PAGE_ALGS_PATH)


async def get_graphql_data(session: aiohttp.ClientSession, url: str, data: dict[str, Any]) -> dict[str, Any]:
    async with session.post(url, json=data) as respons:
        return await respons.json()


async def get_id_solutions(name_alg: str, session: aiohttp.ClientSession,
                           url: str, data: dict[str, Any], totalNum: int) -> list[int]:
    post_data_communitySolutions = {
                'query': query_communitySolutions,
                'variables': {
                    "query": "",
                    "languageTags": [],
                    "topicTags": [],
                    "questionSlug": name_alg, "skip": 0,
                    "first": 0, "orderBy": "hot"},
                'operationName': "communitySolutions"
            }
    id_sols = []
    skip = 0
    first = 100
    while skip < totalNum:
        post_data_communitySolutions['variables']['skip'] = skip
        post_data_communitySolutions['variables']['first'] = first
        communitySolutions_response = await get_graphql_data(
                    session=session, url=url,
                    data=post_data_communitySolutions)
        communitySolutions_response['data']['questionSolutions']['solutions']
        skip += first
    delta = totalNum - skip


async def main():
    for alg in get_alg_url(directory_path=DATA_PAGE_ALGS_PATH):
        path = urlparse(alg['url']).path
        name_alg = path.strip('/').split('/')[-1]
        url = 'https://leetcode.com/graphql/'
        post_data_totalNum = {
            'query': query_tabsStatus,
            'variables': {"titleSlug": name_alg},
            'operationName': "tabsStatus"
        }
        async with aiohttp.ClientSession() as session:
            totalNum_response = await get_graphql_data(session=session, url=url, data=post_data_totalNum)
            totalNum = totalNum_response['data']['questionTopicsList']['totalNum']


if __name__ == "__main__":
    asyncio.run(main())
