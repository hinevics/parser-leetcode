import pathlib


def get_file_path(directory_path: pathlib.PosixPath) -> list[pathlib.PosixPath]:
    # returns a list of all files
    file_list = list(directory_path.glob('*.json'))
    
    for file_path in file_list


def get_alg_url(directory_path: pathlib.PosixPath) -> dict[str, str]:
    # returns a link to the algorithm and the name of the algorithm
    file_path = get_file_path(directory_path)