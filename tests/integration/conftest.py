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


@pytest.fixture(scope="session")
def db_name(load_env): return os.environ["DB_NAME"]


@pytest.fixture(scope="session")
def db_user(load_env): return os.environ["DB_USER"]


@pytest.fixture(scope="session")
def db_password(load_env): return os.environ["DB_PASSWORD"]


@pytest.fixture(scope="session")
def db_host(load_env): return os.environ["DB_HOST"]


@pytest.fixture(scope="session")
def db_port(load_env): return os.environ["DB_PORT"]


@pytest.fixture(scope="session")
def api_server_protocol(load_env): return os.environ["API_SERVER_PROTOCOL"]


@pytest.fixture(scope="session")
def api_server_port(load_env): return os.environ["API_SERVER_PORT"]


@pytest.fixture(scope="session")
def api_server_host(load_env): return  os.environ["API_SERVER_HOST"]


@pytest.fixture(scope="session")
def api_server_url(
    api_server_protocol: str,
    api_server_port: str,
):
    return f"{api_server_protocol}://localhost:{api_server_port}"


@pytest.fixture(scope="session")
def nonogram_server_protocol(load_env): return os.environ["NONOGRAM_SERVER_PROTOCOL"]


@pytest.fixture(scope="session")
def nonogram_server_port(load_env): return os.environ["NONOGRAM_SERVER_PORT"]


@pytest.fixture(scope="session")
def nonogram_server_host(load_env): return os.environ["NONOGRAM_SERVER_HOST"]


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
    
    apiserver_healthcheck_url = f"{api_server_url}/healthcheck/"

    try:
        response = requests.get(apiserver_healthcheck_url)

        return response.status_code == HTTPStatus.OK
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


def testnonogramserver_healthcheck(
    nonogram_server_url: str,
) -> bool:
    
    nonogramserver_healthcheck_url = f"{nonogram_server_url}/healthcheck/"

    try:
        response = requests.get(nonogramserver_healthcheck_url)

        return response.status_code == HTTPStatus.OK
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False



@pytest.fixture(scope='session')
def load_servers(
    load_env,
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

    client = docker.from_env()

    nonogram_server = client.containers.get(nonogram_server_host)
    nonogram_server.exec_run(
        "python src/NonogramServer/manage.py makemigrations"
    )

    nonogram_server.exec_run(
        "python src/NonogramServer/manage.py migrate"
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
