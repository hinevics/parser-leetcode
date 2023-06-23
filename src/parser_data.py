# import glob
import asyncio
import aiohttp
import json
import pathlib

from typing import Any

import graphql_api_queries
from myconfig import URL_API, PATH_DATA
import logger


headers = {
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/113.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json; charset=utf-8'
}

PATH_DATA = pathlib.Path(PATH_DATA)


def saver_data(path: pathlib.PosixPath, name_obj: str, data: dict[str, Any]):
    logger.logger.debug(f'saver_data:{name_obj}')
    path = path.joinpath(name_obj).with_suffix('.json')
    with open(path, mode='w', encoding='utf-8') as file:
        json.dump(data, file)


async def get_graphql_data(session: aiohttp.ClientSession, url: str, data: dict[str, Any]) -> dict[str, Any]:
    async with session.post(url, json=data) as respons:
        return await respons.json()


async def get_total_problems(session: aiohttp.ClientSession, url: str, categorySlug: str) -> int:
    variables = {
        "categorySlug": categorySlug,
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
    logger.logger.debug(f'get_total_problems::total_problems={total_problems}')
    return total_problems


async def get_alg_problems(session: aiohttp.ClientSession, url: str, total_num: int, categorySlug: str) -> list[Any]:
    variables = {
        "categorySlug": categorySlug,
        "limit": total_num,
        "filters": {}
    }
    query_problemset_question_list = {
        'query': graphql_api_queries.query_problemset_question_list,
        'variables': variables,
        'operationName': 'problemsetQuestionList'
    }
    data = await get_graphql_data(
                    session=session, url=url,
                    data=query_problemset_question_list)
    questions = data['data']['problemsetQuestionList']['questions']
    logger.logger.debug(f'get_alg_problems::{len(questions)=}')
    return questions


async def get_total_number_sol(session: aiohttp.ClientSession, url: str, alg_name: str) -> int:
    logger.logger.debug(f'get_total_number_sol::{alg_name}')
    variables = {
        "query": "",
        "languageTags": [],
        "topicTags": [],
        "questionSlug": alg_name,
        "skip": 0,
        "first": 3,
        "orderBy": "hot"}
    query_total_number_sols_for_problem = {
        'query': graphql_api_queries.query_get_total_num_sols,
        'variables': variables,
        "operationName": "communitySolutions"
    }
    data = await get_graphql_data(
        session=session,
        url=url,
        data=query_total_number_sols_for_problem
    )
    totalNum = data['data']['questionSolutions']['totalNum']
    logger.logger.debug(f'get_total_number_sol::{alg_name=}::{totalNum=}')
    return totalNum


def parser_sol(data: dict[str, Any]) -> dict[str, Any]:
    # тут доп процессинг
    return data


async def get_algorithm_solutions(
        session: aiohttp.ClientSession,
        url: str,
        total_num: int,
        alg_name: str
        ) -> list[dict[str, Any]]:
    skip = 0
    first = 100
    variables = {
        "query": "",
        "languageTags": [],
        "topicTags": [],
        "questionSlug": alg_name,
        "skip": skip,
        "first": first,
        "orderBy": "hot"
    }
    query_sols_for_problem = {
        'query': graphql_api_queries.query_algorithm_solutions,
        'variables': variables,
        "operationName": "communitySolutions"
    }
    data = []
    while skip < total_num:
        logger.logger.debug(f'get_algorithm_solutions::{skip=}')
        query_sols_for_problem['variables']['skip'] = skip
        returned_data = await get_graphql_data(
            session=session,
            url=url,
            data=query_sols_for_problem
        )
        data = [
            *data,
            *list(map(parser_sol, returned_data['data']['questionSolutions']['solutions']))
        ]
        skip += first

    skip = 2 * total_num - skip
    logger.logger.debug(f'get_algorithm_solutions::{skip=}')
    query_sols_for_problem['variables']['skip'] = skip
    returned_data = await get_graphql_data(
            session=session,
            url=url,
            data=query_sols_for_problem
        )
    data = [
        *data,
        *list(map(parser_sol, returned_data))
    ]
    return data


async def main():
    path_sol = PATH_DATA.joinpath('sols')
    path_problems = PATH_DATA.joinpath('problems')
    if not path_sol.exists() and not path_problems.exists():
        raise FileExistsError('Папок для хранения нет')

    async with aiohttp.ClientSession() as session:
        total_num = await get_total_problems(session=session, url=URL_API, categorySlug="algorithms")
        algs_data = await get_alg_problems(session=session, url=URL_API, total_num=total_num, categorySlug="algorithms")
        if not algs_data:
            raise ValueError('Пустые данные')
        for alg in algs_data:
            logger.logger.info('START -- get_total_number_sol --')
            total_num_sols = await get_total_number_sol(
                session=session, url=URL_API, alg_name=alg['titleSlug'])
            if not total_num_sols:
                raise ValueError('Пустые данные')
            logger.logger.info('COMPLETED -- get_total_number_sol -- ')

            logger.logger.info('START -- get_algorithm_solutions --')
            sols_alg = await get_algorithm_solutions(
                session=session, url=URL_API, total_num=total_num_sols, alg_name=alg['titleSlug'])
            if not sols_alg:
                raise ValueError('Пустые данные')
            logger.logger.info('COMPLETED -- get_algorithm_solutions -- ')

            alg['sols'] = sols_alg

            logger.logger.info('START -- saver_data --')
            saver_data(data=alg, path=path_problems, name_obj=alg['titleSlug'])
            logger.logger.info('COMPLETED -- saver_data -- ')


if __name__ == "__main__":
    asyncio.run(main())
