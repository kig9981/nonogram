from locust import HttpUser
from locust import task
from locust import between
from locust import events
from locust.runners import MasterRunner
from pathlib import Path
import os
import subprocess
from tests.config import load_env

# locust -f filename --headless -u 100 --run-time 60s -H http://localhost:${nonogram server port}
# locust -f tests/performance/test_nonogram_server/CreateNewSession.py --headless -u 100 --run-time 60s -H http://localhost:8002

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    print("init")
    test_path = Path(os.path.dirname(__file__)).parent.parent
    load_env(test_path)
    docker_compose_file = str(test_path.joinpath("test_docker_compose.yaml"))
    subprocess.call(f"docker compose -f {docker_compose_file} up -d", shell=True)


@events.quit.add_listener
def on_locust_quit(exit_code, **kwargs):
    test_path = Path(os.path.dirname(__file__)).parent.parent
    docker_compose_file = str(test_path.joinpath("test_docker_compose.yaml"))
    subprocess.call(f"docker compose -f {docker_compose_file} down", shell=True)


class CreateNewSessionUser(HttpUser):
    wait_time = between(5, 15)

    @task
    def call(self):
        print("call")
        # with self.client.post("/create_new_session")