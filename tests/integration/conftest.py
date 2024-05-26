import os
import environ
import pytest
import requests
import docker
import psycopg2
from http import HTTPStatus
from psycopg2 import OperationalError


cwd = os.path.dirname(__file__)
env_path = os.path.join(cwd, '.env')

env = environ.Env()
environ.Env.read_env(env_path)


@pytest.fixture(scope='session')
def load_env():
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value



def testdb_healthcheck() -> bool:
    DB_NAME = os.environ["DB_NAME"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_HOST = "localhost"
    DB_PORT = os.environ["DB_PORT"]
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True
    except OperationalError:
        return False
    

def testapiserver_healthcheck() -> bool:
    API_SERVER_PROTOCOL = os.environ["API_SERVER_PROTOCOL"]
    API_SERVER_PORT = os.environ["API_SERVER_PORT"]
    API_SERVER_HOST = "localhost"

    API_SERVER_URL = f"{API_SERVER_PROTOCOL}://{API_SERVER_HOST}:{API_SERVER_PORT}"
    apiserver_healthcheck_url = f"{API_SERVER_URL}/healthcheck/"

    try:
        response = requests.get(apiserver_healthcheck_url)

        return response.status_code == HTTPStatus.OK
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


def testnonogramserver_healthcheck() -> bool:
    NONOGRAM_SERVER_PROTOCOL = os.environ["NONOGRAM_SERVER_PROTOCOL"]
    NONOGRAM_SERVER_PORT = os.environ["NONOGRAM_SERVER_PORT"]
    NONOGRAM_SERVER_HOST = "localhost"

    NONOGRAM_SERVER_URL = f"{NONOGRAM_SERVER_PROTOCOL}://{NONOGRAM_SERVER_HOST}:{NONOGRAM_SERVER_PORT}"
    nonogramserver_healthcheck_url = f"{NONOGRAM_SERVER_URL}/healthcheck/"

    try:
        response = requests.get(nonogramserver_healthcheck_url)

        return response.status_code == HTTPStatus.OK
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False



@pytest.fixture(scope='session')
def load_servers(
    load_env,
    docker_services,
):
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: testdb_healthcheck()
    )

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: testapiserver_healthcheck()
    )

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: testnonogramserver_healthcheck()
    )


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(pytestconfig.rootdir.join(os.path.join("tests", "integration", "test_docker_compose.yaml")))


# @pytest.fixture(scope='session')
# def docker_cleanup():
#     client = docker.from_env()
#     yield
#     try:
#         client.networks.prune()
#         client.containers.prune()
#     except Exception as e:
#         print(f"Error during cleanup: {e}")
