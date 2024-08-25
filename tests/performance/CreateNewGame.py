from locust import HttpUser
from locust import task
from locust import between
from json import JSONDecodeError
from src.utils import Config
import random
import config


response_code_to_str = [
    "GAME_EXIST",
    "NEW_GAME_STARTED",
]


class CreateNewGameUser(HttpUser):
    wait_time = between(0.5, 2)
    user_cnt = 1

    def on_start(self) -> None:
        self.user_num = CreateNewGameUser.user_cnt
        CreateNewGameUser.user_cnt += 1
        with self.client.post("/sessions", json={"client_session_key": f"0.0.0.0_test-agent{self.user_num}"}, catch_response=True) as response:
            try:
                self.session_id = response.json()["session_id"]
                print(f"Sucessfully got session_id: {self.session_id}")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'session_id'")
        return super().on_start()

    @task
    def create_new_game(self):
        with self.client.put(f"/sessions/{self.session_id}", json={"board_id": Config.RANDOM_BOARD}, catch_response=True) as response:
            try:
                board_id = response.json()["board_id"]
                response_code = response.json()["response"]
                
                print(f"Sucessfully got response({response_code_to_str[response_code]}): {board_id}")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'session_id'")

