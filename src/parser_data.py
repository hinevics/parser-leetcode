# import glob
import asyncio
from asyncio import Queue, Semaphore
import aiohttp
import json
import pathlib
import aiofiles

from typing import Any, Coroutine

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


async def saver_data(path: pathlib.PosixPath, name_obj: str, data: dict[str, Any]):
    logger.logger.debug(f'saver_data:{name_obj}')
    path = path.joinpath(name_obj).with_suffix('.json')
    async with aiofiles.open(path, mode='w', encoding='utf-8') as file:
        await file.write(json.dumps(data))


async def retry_on_connection_error(
        function: Coroutine,
        max_attempts: int = 3,
        attempt_delay: int = 5,
        info_: str = None, /,
        *args,
        **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return await function(*args, **kwargs)
        except Exception as e:
            warning_message = (
                f"Communication error. Attempt {attempt}/{max_attempts}," +
                f"\nException: {e}")
            logger.logger.warning(warning_message)
            if attempt == max_attempts:
                message_error = (f'We have a problem in the {function.__name__}.\n'
                                 + f'info: {info_}' + f'Exception: {e}')
                logger.error_logger.error(message_error)
                raise
            await asyncio.sleep(attempt_delay)


async def get_graphql_data(
        session: aiohttp.ClientSession,
        url: str, data: dict[str, Any], sem: Semaphore) -> dict[str, Any]:
    async with sem:
        async with session.post(url, json=data) as respons:
            a = await respons.json()
            return a


async def get_total_problems(
        session: aiohttp.ClientSession,
        url: str, categorySlug: str, sem: Semaphore) -> int:

    variables = {
        "categorySlug": categorySlug,
        "filters": {}
    }
    query_total_number_problems = {
        "query": graphql_api_queries.query_total_problemset_questions,
        "variables": variables,
        "operationName": "problemsetQuestionList"

    }

    try:
        data = await get_graphql_data(
            session=session,
            url=url,
            data=query_total_number_problems,
            sem=sem
        )
    except Exception as e:
        error_message = (
            'We have a problem in the get_total_problems.\n' +
            'The problem occurred with the following attributes:\n' +
            f'{url=}, {query_total_number_problems=}' +
            f'Exception:\n{e}'
        )
        logger.error_logger.error(error_message)

    total_problems = data['data']['problemsetQuestionList']['total']
    logger.logger.debug(f'get_total_problems::total_problems={total_problems}')

    return total_problems


async def get_alg_problems(
        session: aiohttp.ClientSession,
        url: str, total_num: int, categorySlug: str, sem: Semaphore) -> list[Any]:
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

    message_inf = f'{url=}, {total_num=}'
    data = await retry_on_connection_error(
        get_graphql_data, 3, message_inf, session=session, url=url,
        data=query_problemset_question_list, sem=sem)

    questions = data['data']['problemsetQuestionList']['questions']
    logger.logger.debug(f'get_alg_problems::{len(questions)=}')
    return questions


async def get_total_number_sol(session: aiohttp.ClientSession,
                               url: str, alg_name: str, sem: Semaphore) -> int:
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
        data=query_total_number_sols_for_problem,
        sem=sem
    )
    totalNum = data['data']['questionSolutions']['totalNum']
    logger.logger.debug(f'get_total_number_sol::{alg_name=}::{totalNum=}')
    return totalNum


def parser_sol(data: dict[str, Any]) -> dict[str, Any]:
    # тут доп процессинг
    return data


async def get_graphql_data_with_skip(
        session: aiohttp.ClientSession,
        url: str,
        alg_name: str,
        sem: Semaphore,
        skip: int = 0) -> dict[str, Any]:
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
    return await retry_on_connection_error(
        get_graphql_data, 3, session=session, url=url,
        data=query_sols_for_problem, sem=sem)


async def get_algorithm_solutions(
        session: aiohttp.ClientSession,
        url: str,
        total_num: int,
        alg_name: str,
        sem: Semaphore
        ) -> list[dict[str, Any]]:
    data = await asyncio.gather(
        *(get_graphql_data_with_skip(
            session=session,
            url=url,
            alg_name=alg_name,
            skip=i,
            sem=sem
        ) for i in range(0, total_num + 1, 100))
    )

    return data


async def set_algs_data_queue(algs_data: list, queue: Queue, flag: Any):
    for alg in algs_data:
        await queue.put(alg)

    await queue.put(flag)


async def get_sols(
        queue: Queue,
        flag: Any,
        session: aiohttp.ClientSession,
        path_problems: pathlib.PosixPath, sem: Semaphore):
    while (alg := await queue.get()) is not flag:
        logger.logger.info('START -- get_total_number_sol --')
        total_num_sols = await get_total_number_sol(
            session=session, url=URL_API, alg_name=alg['titleSlug'], sem=sem)
        if not total_num_sols:
            raise ValueError('Пустые данные')
        logger.logger.info('COMPLETED -- get_total_number_sol -- ')

        logger.logger.info('START -- get_algorithm_solutions --')
        sols_alg = await get_algorithm_solutions(
            session=session,
            url=URL_API,
            total_num=total_num_sols,
            alg_name=alg['titleSlug'],
            sem=sem
        )
        if not sols_alg:
            raise ValueError('Пустые данные')
        logger.logger.info('COMPLETED -- get_algorithm_solutions -- ')

        alg['sols'] = sols_alg

        logger.logger.info('START -- saver_data --')
        await saver_data(data=alg, path=path_problems, name_obj=alg['titleSlug'])
        logger.logger.info('COMPLETED -- saver_data -- ')


async def main():
    path_sol = PATH_DATA.joinpath('sols')
    path_problems = PATH_DATA.joinpath('problems')
    if not path_sol.exists() and not path_problems.exists():
        raise FileExistsError('Папок для хранения нет')
    queue = Queue()
    sem = Semaphore(50)
    flag = object()
    async with aiohttp.ClientSession() as session:
        total_num = await get_total_problems(
            session=session,
            url=URL_API, categorySlug="algorithms", sem=sem)
        algs_data = await get_alg_problems(
            session=session, url=URL_API, total_num=total_num,
            categorySlug="algorithms", sem=sem)
        if not algs_data:
            raise ValueError('Пустые данные')

        await asyncio.gather(
            get_sols(
                queue=queue,
                session=session,
                path_problems=path_problems,
                flag=flag,
                sem=sem
            ), set_algs_data_queue(algs_data=algs_data, queue=queue, flag=flag))


if __name__ == "__main__":
    asyncio.run(main())
