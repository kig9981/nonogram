import pytest
import json
from typing import Dict
from http import HTTPStatus
from NonogramServer.models import NonogramBoard
from NonogramServer.models import Session
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
    test_sessions,
    add_test_data,
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

    for test_session in test_sessions:
        GAME_NOT_START = 0
        session_id = test_session["session_id"]
        board_id = test_session["board_id"]

        query_dict = {
            "session_id": session_id,
            "board_id": board_id,
            "game_turn": GAME_NOT_START,
        }
        response = send_test_request(
            mock_request=mock_request,
            request_function=get_nonogram_board,
            url=url,
            query_dict=query_dict,
        )

        assert response.status_code == HTTPStatus.OK

        response_data = json.loads(response.content)

        board = NonogramBoard.objects.get(pk=board_id)
        session = Session.objects.get(pk=session_id)

        assert response_data["board"] == board.board
        assert response_data["num_row"] == board.num_row
        assert response_data["num_column"] == board.num_column

        query_dict = {
            "session_id": session_id,
            "board_id": board_id,
            "game_turn": -1,
        }
        response = send_test_request(
            mock_request=mock_request,
            request_function=get_nonogram_board,
            url=url,
            query_dict=query_dict,
        )

        latest_turn = 0 if session.current_game is None else session.current_game.current_turn

        assert response.status_code == HTTPStatus.BAD_REQUEST

        assert response.content.decode() == f"invalid game_turn. must be between 0 to {latest_turn}(latest turn)"


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
