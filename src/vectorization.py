# Converting the text of the solution to a vector. to begin with , blunt
import pathlib
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument




def get_model(path_model: pathlib.PosixPath):
    pass


def load_data(path: pathlib.PosixPath) -> pd.DataFrame:
    pass


def infer_vector(text: list[str]):
    pass


def main():
    """_summary_
    """
    tagged_documents = [TaggedDocument(words=doc.split(), tags=[str(i)]) for i, doc in enumerate(documents)]


if __name__ == '__main__':
    main()
