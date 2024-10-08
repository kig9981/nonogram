from locust import events
from locust.runners import MasterRunner
from locust.runners import LocalRunner
from pathlib import Path
import os
import time
import subprocess
from tests.config import load_env
from tests.config import testdb_healthcheck
from tests.config import testnonogramserver_healthcheck


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, LocalRunner):
        @events.quit.add_listener
        def on_locust_quit(exit_code, **kwargs):
            print("finishing...")
            test_condition = os.environ["TEST_CONDITION"]
            if test_condition == "local":
                test_path = Path(os.path.dirname(__file__)).parent
                docker_compose_file = str(test_path.joinpath("test_docker_compose.yaml"))
                subprocess.call(f"docker compose -f {docker_compose_file} down", shell=True)

        print("initializing...")
        test_path = Path(os.path.dirname(__file__)).parent
        load_env(test_path)
        test_condition = os.environ["TEST_CONDITION"]
        if test_condition == "local":
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
