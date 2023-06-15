# to begin with, we simply collect all the solutions in one dataset in csv format
import pandas as pd
import json
import pathlib
import glob

from typing import Any

import logger
from myconfig import PATH_DATA


PATH_DATA_PROBLEMS = pathlib.Path(PATH_DATA).joinpath('problems')
PATH_DATA_SOLS = pathlib.Path(PATH_DATA).joinpath('sols')


def laod_file(directory_path: pathlib.PosixPath) -> dict[str, Any]:
    if not directory_path.exists():
        raise FileNotFoundError('Такой директории нет!')
    file_path_list = glob.glob(str(directory_path / '*'))
    for fp in file_path_list:
        logger.logger.debug(f"laod_file::{fp}")
        with open(fp, mode='r', encoding='utf-8') as file:
            data = json.load(file)
            yield data


def parser_json(data: dict[str, Any]) -> pd.DataFrame:
    data_for_pandas = {
        'id_sol': [],
        'title_sol': [],
        'commentCount': [],
        'topLevelCommentCount': [],
        'viewCount': [],
        'solutionTags': [],
        'post_id': [],
        'post_content': [],
    }
    for sol in data['sols']:
        logger.logger.debug(f"parser_json::{sol['id']}")
        data_for_pandas['id_sol'].append(sol['id'])
        data_for_pandas['title_sol'].append(sol['title'])
        data_for_pandas['commentCount'].append(sol['commentCount'])
        data_for_pandas['topLevelCommentCount'].append(sol['topLevelCommentCount'])
        data_for_pandas['viewCount'].append(sol['viewCount'])
        solutionTags = list(map(lambda x: x['name'], data['sols'][0]['solutionTags']))
        data_for_pandas['solutionTags'].append(solutionTags)
        data_for_pandas['post_id'].append(sol['post']['id'])
        data_for_pandas['post_content'].append(sol['post']['content'])
    return pd.DataFrame(data_for_pandas)


def saver_data(data: pd.DataFrame, path: pathlib.PosixPath, name: str):
    logger.logger.debug(f'saver_data"::{name}')
    if not path.exists():
        raise FileNotFoundError('Такой директории нет!')
    path = path.joinpath(name).with_suffix('.csv')
    data.to_csv(path)


if __name__ == "__main__":
    for jd in laod_file(PATH_DATA_PROBLEMS):
        logger.logger.info('START -- parsing data -- ')
        data = parser_json(jd)
        logger.logger.info('COMPLETED -- parsing data -- ')
        logger.logger.info('START -- saving data -- ')
        saver_data(data, PATH_DATA_SOLS, name=jd['titleSlug'])
        logger.logger.info('COMPLETED -- saving data -- ')
