from locust import HttpUser
from locust import task
from locust import between
from json import JSONDecodeError
from src.utils import Config
import random


response_code_to_str = [
    "GAME_EXIST",
    "NEW_GAME_STARTED",
]


class GamePlayUser(HttpUser):
    wait_time = between(0.5, 2)
    user_cnt = 1

    def on_start(self) -> None:
        self.user_num = GamePlayUser.user_cnt
        GamePlayUser.user_cnt += 1
        self.client.headers.update({"User-Agent": f"test-agent{self.user_num}"})
        with self.client.post("/sessions", catch_response=True) as response:
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
                json_response = response.json()
                board_id = json_response["board_id"]
                response_code = json_response["response"]

                num_row, num_column = json_response["num_row"], json_response["num_column"]

                print(f"Sucessfully got response({response_code_to_str[response_code]}): {board_id}")
                
                move_pool = [(x, y) for x in range(num_row) for y in range(num_column)]

                random.shuffle(move_pool)

                for x, y in move_pool:
                    with self.client.post(
                        url=f"/sessions/{self.session_id}/move",
                        json={
                            "x": x,
                            "y": y,
                            "state": random.randint(
                                Config.GAME_BOARD_CELL_STATE_LOWERBOUND,
                                Config.GAME_BOARD_CELL_STATE_UPPERBOUND,
                            )
                        },
                    ) as response:
                        response = response.json()["response"]
                        print(f"Sucessfully got response({response})")
                
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'session_id'")
