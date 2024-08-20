from pathlib import Path
import os
import requests
import psycopg2
from http import HTTPStatus
from psycopg2 import OperationalError


def load_env(env_path: Path):
    env_path = env_path.joinpath('test.env')
    if env_path.exists():
        with env_path.open() as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


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