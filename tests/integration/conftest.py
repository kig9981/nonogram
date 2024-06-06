import os
import json
import pytest
import requests
import psycopg2
from http import HTTPStatus
from psycopg2 import OperationalError


def load_env():
    cwd = os.path.dirname(__file__)
    env_path = os.path.join(cwd, 'test.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def pytest_configure():
    load_env()


@pytest.fixture(scope="session")
def db_name():
    return os.environ["DB_NAME"]


@pytest.fixture(scope="session")
def db_user():
    return os.environ["DB_USER"]


@pytest.fixture(scope="session")
def db_password():
    return os.environ["DB_PASSWORD"]


@pytest.fixture(scope="session")
def db_host():
    return os.environ["DB_HOST"]


@pytest.fixture(scope="session")
def db_port():
    return os.environ["DB_PORT"]


@pytest.fixture(scope="session")
def api_server_protocol():
    return os.environ["API_SERVER_PROTOCOL"]


@pytest.fixture(scope="session")
def api_server_port():
    return os.environ["API_SERVER_PORT"]


@pytest.fixture(scope="session")
def api_server_host():
    return os.environ["API_SERVER_HOST"]


@pytest.fixture(scope="session")
def api_server_url(
    api_server_protocol: str,
    api_server_port: str,
):
    return f"{api_server_protocol}://localhost:{api_server_port}"


@pytest.fixture(scope="session")
def nonogram_server_protocol():
    return os.environ["NONOGRAM_SERVER_PROTOCOL"]


@pytest.fixture(scope="session")
def nonogram_server_port():
    return os.environ["NONOGRAM_SERVER_PORT"]


@pytest.fixture(scope="session")
def nonogram_server_host():
    return os.environ["NONOGRAM_SERVER_HOST"]


@pytest.fixture(scope="session")
def nonogram_server_url(
    nonogram_server_protocol: str,
    nonogram_server_port: str,
):
    return f"{nonogram_server_protocol}://localhost:{nonogram_server_port}"


def testdb_healthcheck(
    db_name: str,
    db_user: str,
    db_password: str,
    db_port: str,
) -> bool:
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host="localhost",
            port=db_port,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True
    except OperationalError:
        return False


def testapiserver_healthcheck(
    api_server_url: str,
) -> bool:
    apiserver_healthcheck_url = f"{api_server_url}/healthcheck"

    try:
        response = requests.get(apiserver_healthcheck_url)

        return response.status_code == HTTPStatus.OK
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


def testnonogramserver_healthcheck(
    nonogram_server_url: str,
) -> bool:
    nonogramserver_healthcheck_url = f"{nonogram_server_url}/healthcheck"

    try:
        response = requests.get(nonogramserver_healthcheck_url)

        return response.status_code == HTTPStatus.OK
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


@pytest.fixture(scope='session')
def load_servers(
    docker_services,
    db_name: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: str,
    api_server_url: str,
    nonogram_server_host: str,
    nonogram_server_url: str,
):
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: testdb_healthcheck(
            db_name,
            db_user,
            db_password,
            db_port,
        ),
    )

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: testapiserver_healthcheck(
            api_server_url,
        ),
    )

    docker_services.wait_until_responsive(
        timeout=60.0,
        pause=0.1,
        check=lambda: testnonogramserver_healthcheck(
            nonogram_server_url,
        ),
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
