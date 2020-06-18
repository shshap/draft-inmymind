"""docstring explaines module"""
import logging

from inmymind.dbrestapi._dbrestapi_utils import find_api_service, find_db_service

logger = logging.getLogger(__name__)


def run_api_server_by_urls(api_url, db_url):
    api_service = find_api_service(api_url)
    db_service = find_db_service(db_url)
    api_service(db_service)


if __name__ == '__main__':
    run_api_server_by_urls('http://0.0.0.0:50001?framework=flaskrestful&debug=True&use_reloader=True',
                           'mongo://localhost:27017/inmymind?alias=core')
