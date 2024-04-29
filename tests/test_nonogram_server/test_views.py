import pytest
import json
import os
from typing import Dict
from http import HTTPStatus
from NonogramServer.views import get_nonogram_board
from NonogramServer.views import set_cell_state
from NonogramServer.views import create_new_session
from NonogramServer.views import create_new_game
from django.test.client import RequestFactory
from django.http import HttpResponse


BOARD_ID_UNUSED_FOR_TEST = -1


@pytest.fixture
def mock_request():
    return RequestFactory()


def send_test_request(
    mock_request: RequestFactory,
    request_function,
    url: str,
    query_dict: Dict[str, object],
) -> HttpResponse:
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = request_function(request)

    return response


@pytest.mark.django_db
def test_get_nonogram_board(
    mock_request: RequestFactory,
    test_boards,
):
    url = '/get_nonogram_board/'

    query_dict = {
        "session_id": 0,
        "board_id": BOARD_ID_UNUSED_FOR_TEST,
    }

    response = send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.content.decode() == f"board_id {BOARD_ID_UNUSED_FOR_TEST} not found."

    for test_board in test_boards:
        query_dict = {
            "session_id": 0,
            "board_id": test_board['board_id'],
        }
        response = send_test_request(
            mock_request=mock_request,
            request_function=get_nonogram_board,
            url=url,
            query_dict=query_dict,
        )

        assert response.status_code == HTTPStatus.OK

        response_data = json.loads(response.content)

        assert response_data["board"] == test_board["board"]
        assert response_data["num_row"] == test_board["num_row"]
        assert response_data["num_column"] == test_board["num_column"]


@pytest.mark.django_db
def test_set_cell_state(mock_request: RequestFactory):
    url = '/set_cell_state/'
    query_dict = {"session_id": 0}
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = set_cell_state(request)
    assert response.content == b"set_cell_state(post)"


@pytest.mark.django_db
def test_create_new_session(mock_request: RequestFactory):
    url = '/create_new_session/'
    query_dict = {"session_id": 0}
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = create_new_session(request)
    assert response.content == b"create_new_session(post)"


@pytest.mark.django_db
def test_create_new_game(mock_request: RequestFactory):
    url = '/create_new_game/'
    query_dict = {"session_id": 0}
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = create_new_game(request)
    assert response.content == b"create_new_game(post)"
