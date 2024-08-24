from locust import HttpUser
from locust import task
from locust import between
from json import JSONDecodeError
import random
import tests.performance.config


class CreateNewSessionUser(HttpUser):
    wait_time = between(0.5, 2)

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
