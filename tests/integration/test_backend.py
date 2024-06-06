import os
import io
import base64
import pytest
import requests
from http import HTTPStatus
from PIL import Image
from typing import List


@pytest.fixture(scope="session")
def image_datas():
    cwd = os.path.dirname(__file__)
    test_image_path = os.path.join(cwd, 'test_data.png')
    with Image.open(test_image_path) as img:
        byte_image = io.BytesIO()
        img.save(byte_image, format="JPEG")
        b64_image = base64.b64encode(byte_image.getvalue()).decode()
    return [b64_image]


def test_add_new_board(
    load_servers,
    api_server_url: str,
    nonogram_server_url: str,
    image_datas: List[str],
):
    response = requests.get(f"{api_server_url}/healthcheck")
    assert response.status_code == HTTPStatus.OK

    response = requests.get(f"{nonogram_server_url}/healthcheck")
    assert response.status_code == HTTPStatus.OK

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

        response = requests.post(
            f"{nonogram_server_url}/nonogram/{board_id}",
            json={
                "session_id": 0,
                "board_id": board_id,
            }
        )

        assert response.status_code == HTTPStatus.OK

        response = response.json()
