import os
import environ
import pytest
import requests
from http import HTTPStatus


cwd = os.path.dirname(__file__)

env = environ.Env()
environ.Env.read_env(os.path.join(cwd, '.env'))


DB_NAME = env("DB_NAME")
DB_USER = env("DB_USER")
DB_PASSWORD = env("DB_PASSWORD")
DB_HOST = env("DB_HOST")
DB_PORT = env("DB_PORT")

NONOGRAM_SERVER_PROTOCOL = env("NONOGRAM_SERVER_PROTOCOL")
NONOGRAM_SERVER_HOST = env("NONOGRAM_SERVER_HOST")
NONOGRAM_SERVER_PORT = env("NONOGRAM_SERVER_PORT")

API_SERVER_PROTOCOL = env("NONOGRAM_SERVER_PROTOCOL")
API_SERVER_HOST = env("API_SERVER_HOST")
API_SERVER_PORT = env("NONOGRAM_SERVER_PORT")

NONOGRAM_SERVER_URL = f"{NONOGRAM_SERVER_PROTOCOL}://{NONOGRAM_SERVER_HOST}:{NONOGRAM_SERVER_PORT}"
API_SERVER_URL = f"{API_SERVER_PROTOCOL}://{API_SERVER_HOST}:{API_SERVER_PORT}"
    

def testapiserver_healthcheck() -> bool:
    apiserver_healthcheck_url = f"{API_SERVER_URL}/healthcheck"

    try:
        response = requests.get(apiserver_healthcheck_url)

        return response.status_code == HTTPStatus.OK
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


def testnonogramserver_healthcheck() -> bool:
    nonogramserver_healthcheck_url = f"{NONOGRAM_SERVER_URL}/healthcheck"

    try:
        response = requests.get(nonogramserver_healthcheck_url)

        return response.status_code == HTTPStatus.OK
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False



@pytest.fixture(scope='session')
def load_servers(
    docker_services,
):

    docker_services.wait_until_responsive(
        timeout=300.0,
        pause=0.1,
        check=lambda: testapiserver_healthcheck()
    )

    docker_services.wait_until_responsive(
        timeout=300.0,
        pause=0.1,
        check=lambda: testnonogramserver_healthcheck()
    )


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(pytestconfig.rootdir.join(os.path.join("tests", "integration", "test_docker_compose.yaml")))
