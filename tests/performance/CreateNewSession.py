from locust import HttpUser
from locust import task
from locust import between
from json import JSONDecodeError
import random
import config


class CreateNewSessionUser(HttpUser):
    wait_time = between(0.5, 2)

    @task
    def single_session_id(self):
        self.client.headers.update({"User-Agent": "test-agent"})
        with self.client.post("/sessions", catch_response=True) as response:
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
        self.client.headers.update({"User-Agent": f"test-agent{random_number}"})
        with self.client.post("/sessions", catch_response=True) as response:
            try:
                session_id = response.json()["session_id"]
                print(f"Sucessfully got session_id: {session_id}")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'session_id'")
