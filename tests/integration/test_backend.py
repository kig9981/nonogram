import os
import pytest
import requests
from http import HTTPStatus


def test(
    load_servers,
    api_server_url: str,
    nonogram_server_url: str,
):
    response = requests.get(f"{api_server_url}/healthcheck/")
    assert response.status_code == HTTPStatus.OK

    response = requests.get(f"{nonogram_server_url}/healthcheck/")
    assert response.status_code == HTTPStatus.OK