import logger
import requests
import glob

import graphql_api_queries
from myconfig import URL_API


headers = {
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json'
}


def main():
    variables = {
        "categorySlug": "algorithms",
        "skip": 0,
        "limit": 50,
        "filters": {}
    }
    query = {
        "query": graphql_api_queries.problemsetQuestionListQuery,
        "variables": variables,
        "operationName": "problemsetQuestionList"

    }
    response = requests.post(URL_API, headers=headers, json=query)
    if response.status_code == 200:
        # result = response.json()
        print(response.text)
        # Обработка данных из result
    else:
        print('Ошибка при выполнении запроса')


if __name__ == "__main__":
    main()
