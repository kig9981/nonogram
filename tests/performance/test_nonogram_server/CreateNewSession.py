from locust import HttpUser
from locust import task
from locust import between
from locust import events
from locust.runners import MasterRunner
from locust.runners import LocalRunner
from pathlib import Path
from json import JSONDecodeError
import os
import time
import random
import subprocess
from tests.config import load_env
from tests.config import testdb_healthcheck
from tests.config import testnonogramserver_healthcheck


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, LocalRunner):
        print("initializing...")
        test_path = Path(os.path.dirname(__file__)).parent.parent
        load_env(test_path)
        docker_compose_file = str(test_path.joinpath("test_docker_compose.yaml"))
        subprocess.call(f"docker compose -f {docker_compose_file} up -d", shell=True)

        print("waiting for db to be initialized...")

        while not testdb_healthcheck(
            db_name=os.environ["DB_NAME"],
            db_user=os.environ["DB_USER"],
            db_password=os.environ["DB_PASSWORD"],
            db_port=os.environ["DB_PORT"],
        ):
            time.sleep(0.1)

        print("waiting for nonogram server to be initialized...")

        nonogram_server_protocol = os.environ["NONOGRAM_SERVER_PROTOCOL"]
        nonogram_server_port = os.environ["NONOGRAM_SERVER_PORT"]

        nonogram_server_url = f"{nonogram_server_protocol}://localhost:{nonogram_server_port}"

        while not testnonogramserver_healthcheck(nonogram_server_url):
            time.sleep(0.1)

        print("initialization is done")


@events.quitting.add_listener
def on_locust_quit(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, LocalRunner):
        test_path = Path(os.path.dirname(__file__)).parent.parent
        docker_compose_file = str(test_path.joinpath("test_docker_compose.yaml"))
        subprocess.call(f"docker compose -f {docker_compose_file} down", shell=True)


class CreateNewSessionUser(HttpUser):
    wait_time = between(5, 15)

    @task
    def single_session_id(self):
        with self.client.post("/sessions", json={"client_session_key": "0.0.0.0_test-agent"}, catch_response=True) as response:
            try:
                session_id = response.json()["session_id"]
                print(f"Sucessfully got session_id: {session_id}")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'session_id'")

    @task
    def random_session_id(self):
        random_number = random.randint(0, 1000000000)
        with self.client.post("/sessions", json={"client_session_key": f"0.0.0.0_test-agent{random_number}"}, catch_response=True) as response:
            try:
                session_id = response.json()["session_id"]
                print(f"Sucessfully got session_id: {session_id}")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'session_id'")
