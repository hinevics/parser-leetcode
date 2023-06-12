# import glob
import asyncio
import aiohttp

from typing import Any

import graphql_api_queries
from myconfig import URL_API
import logger


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


async def get_total_problems(session: aiohttp.ClientSession, url: str) -> int:
    logger.logger.info('Start get_total_problems')
    variables = {
        "categorySlug": "algorithms",
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
    logger.logger.info('Completed get_total_problems')
    return total_problems


async def get_alg_problems(session: aiohttp.ClientSession, url: str, total_num: int) -> list[Any]:
    logger.logger.info('Start get_alg_problems')
    skip = 0
    limit = 50
    variables = {
        "categorySlug": "algorithms",
        "skip": skip,
        "limit": limit,
        "filters": {}
    }
    query_problemset_question_list = {
        'query': graphql_api_queries.query_problemset_question_list,
        'variables': variables,
        'operationName': 'problemsetQuestionList'
    }
    data = []
    while skip < total_num:
        logger.logger.debug(f'Load {skip}, {limit}')
        query_problemset_question_list['variables']['skip'] = skip
        questions = await get_graphql_data(
                    session=session, url=url,
                    data=query_problemset_question_list)
        data = [
            *data,
            *questions['data']['problemsetQuestionList']['questions']
        ]
        skip += limit
    limit = skip - total_num
    skip = total_num - limit
    print(f'{first=}')
    print(f'{skip=}')

    logger.logger.debug(f'Load last {total_num -skip}')
    query_problemset_question_list['variables']['skip'] = skip
    query_problemset_question_list['variables']['limit'] = limit
    print(query_problemset_question_list)
    questions = await get_graphql_data(
                    session=session, url=url,
                    data=query_problemset_question_list)
    print(f"{len(questions['data']['problemsetQuestionList']['questions'])=}")
    data = [
            *data,
            *questions['data']['problemsetQuestionList']['questions']
        ]
    logger.logger.info('Completed get_alg_problems')
    return data


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
        total_num = await get_total_problems(session=session, url=URL_API)
        algs_data = await get_alg_problems(session=session, url=URL_API, total_num=total_num)
        print(total_num)

        print(len(algs_data))


if __name__ == "__main__":
    asyncio.run(main())
