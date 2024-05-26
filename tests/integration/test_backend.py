import os
import requests
from http import HTTPStatus


DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]

NONOGRAM_SERVER_PROTOCOL = os.environ["NONOGRAM_SERVER_PROTOCOL"]
NONOGRAM_SERVER_PORT = os.environ["NONOGRAM_SERVER_PORT"]

API_SERVER_PROTOCOL = os.environ["API_SERVER_PROTOCOL"]
API_SERVER_PORT = os.environ["API_SERVER_PORT"]

NONOGRAM_SERVER_URL = f"{NONOGRAM_SERVER_PROTOCOL}://localhost:{NONOGRAM_SERVER_PORT}"
API_SERVER_URL = f"{API_SERVER_PROTOCOL}://localhost:{API_SERVER_PORT}"


def test(load_servers):
    response = requests.get(f"{NONOGRAM_SERVER_URL}/healthcheck/")
    assert response.status_code == HTTPStatus.OK