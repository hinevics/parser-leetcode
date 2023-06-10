# import logger
# import glob
import json
import asyncio
import aiohttp

from typing import Any

import graphql_api_queries
from myconfig import URL_API


headers = {
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/113.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json; charset=utf-8'
}


async def get_graphql_data(session: aiohttp.ClientSession, url: str, data: dict[str, Any]) -> dict[str, Any]:
    async with session.post(url, json=data) as respons:
        return await respons.json()


async def get_name_problems(session: aiohttp.ClientSession, url: str) -> list[str]:
    variables = {
        "categorySlug": "",
        "filters": {}
    }
    query_total_number_problems = {
        "query": graphql_api_queries.query_total_problemset_questions,
        "variables": variables,
        "operationName": "problemsetQuestionList"

    }
    data = await get_graphql_data(
        session=session,
        url=url,
        data=query_total_number_problems
    )
    total_problems = data['data']['problemsetQuestionList']['total']
    print(total_problems)


async def main():
    # variables = {
    #     "categorySlug": "algorithms",
    #     "skip": 0,
    #     "limit": 50,
    #     "filters": {}
    # }
    # query = {
    #     "query": graphql_api_queries.problemsetQuestionListQuery,
    #     "variables": variables,
    #     "operationName": "problemsetQuestionList"

    # }

    async with aiohttp.ClientSession() as session:
        await get_name_problems(session=session, url=URL_API)


if __name__ == "__main__":
    asyncio.run(main())
