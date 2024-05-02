import pytest
import json
from typing import Any
from typing import List
from typing import Dict
from typing import Callable
from http import HTTPStatus
from NonogramServer.models import NonogramBoard
from NonogramServer.models import Session
from NonogramServer.views import get_nonogram_board
from NonogramServer.views import set_cell_state
from NonogramServer.views import create_new_session
from NonogramServer.views import create_new_game
from Nonogram.utils import GameBoardCellState
from Nonogram.utils import deserialize_gameboard
from Nonogram.utils import deserialize_gameplay
from Nonogram.NonogramBoard import NonogramGameplay
from Nonogram.RealGameBoard import RealGameBoard
from django.test.client import RequestFactory
from django.http import HttpRequest
from django.http import HttpResponse


BOARD_ID_UNUSED_FOR_TEST = -1
SESSION_ID_UNUSED_FOR_TEST = -1
BOARD_QUERY = 0


@pytest.fixture
def mock_request():
    return RequestFactory()


async def send_test_request(
    mock_request: RequestFactory,
    request_function: Callable[[HttpRequest], HttpResponse],
    url: str,
    query_dict: Dict[str, Any],
) -> HttpResponse:
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = await request_function(request)

    return response


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_board_for_get_nonogram_board(
    mock_request: RequestFactory,
    test_boards: List[Dict[str, Any]],
    add_test_data,
):
    url = '/get_nonogram_board/'

    for test_board in test_boards:
        query_dict = {
            "session_id": BOARD_QUERY,
            "board_id": test_board['board_id'],
        }
        response = await send_test_request(
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


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_session_for_get_nonogram_board(
    mock_request: RequestFactory,
    test_sessions: List[Dict[str, Any]],
    add_test_data,
):
    url = '/get_nonogram_board/'

    for test_session in test_sessions:
        GAME_NOT_START = 0
        session_id = test_session["session_id"]
        board_id = test_session["board_id"]

        query_dict = {
            "session_id": session_id,
        }

        response = await send_test_request(
            mock_request=mock_request,
            request_function=get_nonogram_board,
            url=url,
            query_dict=query_dict,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode() == "'game_turn' is missing."

        query_dict = {
            "session_id": session_id,
            "game_turn": GAME_NOT_START,
        }
        response = await send_test_request(
            mock_request=mock_request,
            request_function=get_nonogram_board,
            url=url,
            query_dict=query_dict,
        )

        assert response.status_code == HTTPStatus.OK

        response_data = json.loads(response.content)

        board = await NonogramBoard.objects.aget(pk=board_id)
        session = await Session.objects.select_related('current_game').aget(pk=session_id)

        assert response_data["board"] == board.board
        assert response_data["num_row"] == board.num_row
        assert response_data["num_column"] == board.num_column

        query_dict = {
            "session_id": session_id,
            "game_turn": -1,
        }
        response = await send_test_request(
            mock_request=mock_request,
            request_function=get_nonogram_board,
            url=url,
            query_dict=query_dict,
        )

        latest_turn = 0 if session.current_game is None else session.current_game.current_turn

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode() == f"invalid game_turn. must be between 0 to {latest_turn}(latest turn)"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_history_for_get_nonogram_board(
    mock_request: RequestFactory,
    test_histories: List[Dict[str, Any]],
    add_test_data,
):
    url = '/get_nonogram_board/'

    for test_history in test_histories:
        session_id = test_history["session_id"]
        for cur_turn, move in enumerate(test_history["moves"]):
            query_dict = {
                "session_id": session_id,
                "game_turn": cur_turn + 1,
            }
            response = await send_test_request(
                mock_request=mock_request,
                request_function=get_nonogram_board,
                url=url,
                query_dict=query_dict,
            )

            assert response.status_code == HTTPStatus.OK

            applied_board = move["board"]
            response_data = json.loads(response.content)

            assert response_data["board"] == applied_board


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_nonogram_board(
    mock_request: RequestFactory,
    add_test_data,
):
    url = '/get_nonogram_board/'

    query_dict = {}

    response = await send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == "'session_id' is missing."

    query_dict = {
        "session_id": BOARD_QUERY,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == "'board_id' is missing."

    query_dict = {
        "session_id": BOARD_QUERY,
        "board_id": BOARD_ID_UNUSED_FOR_TEST,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.content.decode() == f"board_id {BOARD_ID_UNUSED_FOR_TEST} not found."


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_session_for_set_cell_state(
    mock_request: RequestFactory,
    test_sessions: List[Dict[str, Any]],
    add_test_data,
):
    url = '/set_cell_state/'

    moves = [
        GameBoardCellState.NOT_SELECTED,
        GameBoardCellState.MARK_X,
        GameBoardCellState.MARK_QUESTION,
        GameBoardCellState.REVEALED,
        GameBoardCellState.NOT_SELECTED,
        GameBoardCellState.MARK_X,
        GameBoardCellState.MARK_QUESTION,
    ]

    for test_session in test_sessions:
        session_id = test_session["session_id"]
        board_id = test_session["board_id"]

        board_data = await NonogramBoard.objects.aget(pk=board_id)

        real_board = RealGameBoard(
            board_id=board_id,
            board=deserialize_gameboard(board_data.board)
        )

        play = NonogramGameplay(
            board_id=board_id,
            board=real_board,
        )
        session = await Session.objects.aget(pk=session_id)
        play.playboard = deserialize_gameplay(session.board)

        for x in range(play.num_row):
            for y in range(play.num_column):
                for new_state in moves:
                    expected_result = play.mark(x, y, new_state)
                    query_dict = {
                        "session_id": session_id,
                        "x_coord": x,
                        "y_coord": y,
                        "new_state": new_state,
                    }

                    response = await send_test_request(
                        mock_request=mock_request,
                        request_function=set_cell_state,
                        url=url,
                        query_dict=query_dict,
                    )

                    assert response.status_code == HTTPStatus.OK

                    response_data = json.loads(response.content)

                    assert response_data["response"] == expected_result


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_set_cell_state(
    mock_request: RequestFactory,
    add_test_data,
):
    url = '/set_cell_state/'
    query_dict = {}

    response = await send_test_request(
        mock_request=mock_request,
        request_function=set_cell_state,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == "'session_id' is missing."

    query_dict = {
        "session_id": SESSION_ID_UNUSED_FOR_TEST,
        "x_coord": 0,
        "y_coord": 0,
        "new_state": GameBoardCellState.NOT_SELECTED,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=set_cell_state,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.content.decode() == f"session_id {SESSION_ID_UNUSED_FOR_TEST} not found."


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_create_new_session(mock_request: RequestFactory):
    url = '/create_new_session/'
    query_dict = {"session_id": 0}
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = await create_new_session(request)
    assert response.content == b"create_new_session(post)"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_create_new_game(mock_request: RequestFactory):
    url = '/create_new_game/'
    query_dict = {"session_id": 0}
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = await create_new_game(request)
    assert response.content == b"create_new_game(post)"
