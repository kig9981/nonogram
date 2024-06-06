import os
import io
import json
import base64
import pytest
import requests
from http import HTTPStatus
from PIL import Image
from typing import List
from typing import Dict
from typing import Any


@pytest.fixture(scope="session")
def backend_testdatas():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'backend_testdata.json')
    with open(test_data_path, 'r') as f:
        test_datas = json.load(f)

    return test_datas


@pytest.fixture(scope="session")
def image_datas():
    cwd = os.path.dirname(__file__)
    test_image_path = os.path.join(cwd, 'test_data.png')
    with Image.open(test_image_path) as img:
        byte_image = io.BytesIO()
        img.save(byte_image, format="PNG")
        b64_image = base64.b64encode(byte_image.getvalue()).decode()
    return [b64_image]


def test_add_new_board(
    load_servers,
    nonogram_server_url: str,
    image_datas: List[str],
):

    for b64_image in image_datas:
        response = requests.post(
            f"{nonogram_server_url}/nonogram",
            json={
                "board": b64_image,
                "num_row": 20,
                "num_column": 20,
                "theme": "test data"
            }
        )

        assert response.status_code == HTTPStatus.OK

        response = response.json()

        board_id = response["board_id"]

        response = requests.get(
            f"{nonogram_server_url}/nonogram/{board_id}",
        )

        assert response.status_code == HTTPStatus.OK

        response = response.json()


def test_game(
    load_servers,
    api_server_url: str,
    nonogram_server_url: str,
    backend_testdatas: List[Dict[str, Any]],
):
    NEW_GAME_STARTED = 1
    for test_data in backend_testdatas:
        board = test_data["board"]
        moves = test_data["moves"]
        num_row = len(board)
        num_column = len(board[0])
        board_image = Image.new(mode="1", size=(num_row, num_column))

        for x in range(num_row):
            for y in range(num_column):
                board_image.putpixel((x, y), (1 - board[x][y]) * 255)

        byte_image = io.BytesIO()
        board_image.save(byte_image, "PNG")
        b64_image = base64.b64encode(byte_image.getvalue()).decode()

        response = requests.post(
            f"{nonogram_server_url}/nonogram",
            json={
                "board": b64_image,
                "num_row": num_row,
                "num_column": num_column,
                "theme": "test data"
            }
        )

        assert response.status_code == HTTPStatus.OK

        response = response.json()

        board_id = response["board_id"]

        response = requests.post(
            f"{api_server_url}/sessions",
        )

        assert response.status_code == HTTPStatus.OK

        response = response.json()

        session_id = response["session_id"]

        response = requests.post(
            f"{api_server_url}/sessions/{session_id}",
            json={
                "board_id": board_id,
            }
        )

        assert response.status_code == HTTPStatus.OK

        response = response.json()

        assert response["response"] == NEW_GAME_STARTED
        assert response["board_id"] == board_id
        assert response["board"] == board
        assert response["num_row"] == num_row
        assert response["num_column"] == num_column

        for move in moves:
            x = move["x"]
            y = move["y"]
            state = move["state"]
            expected_response = move["response"]

            response = requests.post(
                f"{api_server_url}/sessions/{session_id}/move",
                json={
                    "x": x,
                    "y": y,
                    "state": state,
                }
            )

            assert response.status_code == HTTPStatus.OK

            response = response.json()

            assert expected_response == response["response"]
