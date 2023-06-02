import pathlib
import json


def get_file_path(directory_path: pathlib.PosixPath) -> list[pathlib.PosixPath]:
    # returns a list of all files
    file_list = list(directory_path.glob('*.json'))
    for file_path in file_list:
        yield file_path


def get_alg_url(directory_path: pathlib.PosixPath) -> dict[str, str]:
    # returns a link to the algorithm and the name of the algorithm
    file_path = get_file_path(directory_path)
    for fp in file_path:
        with open(file=fp, mode='r', encoding='utf-8') as file:
            algs_list = json.load(file)
            for alg in algs_list:
                yield alg
