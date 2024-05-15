import pytest
import json
import uuid
import os
import io
import base64
from typing import Any
from typing import List
from typing import Dict
from http import HTTPStatus
from NonogramServer.models import NonogramBoard
from NonogramServer.models import Session
from NonogramServer.views.GetNonogramBoard import GetNonogramBoard
from NonogramServer.views.SetCellState import SetCellState
from NonogramServer.views.CreateNewSession import CreateNewSession
from NonogramServer.views.CreateNewGame import CreateNewGame
from NonogramServer.views.AddNonogramBoard import AddNonogramBoard
from src.utils import GameBoardCellState
from src.utils import deserialize_gameboard
from src.utils import deserialize_gameplay
from src.utils import is_uuid4
from Nonogram.NonogramBoard import NonogramGameplay
from Nonogram.RealGameBoard import RealGameBoard
from django.core.exceptions import ObjectDoesNotExist
from django.test.client import RequestFactory
from PIL import Image
from ..util import send_test_request


BOARD_ID_UNUSED_FOR_TEST = str(uuid.uuid4())
SESSION_ID_UNUSED_FOR_TEST = str(uuid.uuid4())
INCORRECT_ID = "xxxxxxx"
BOARD_QUERY = 0
GAME_NOT_START = 0
RANDOM_BOARD = 0
GAME_EXIST = 0
NEW_GAME_STARTED = 1

get_nonogram_board = GetNonogramBoard.as_view()
set_cell_state = SetCellState.as_view()
create_new_session = CreateNewSession.as_view()
create_new_game = CreateNewGame.as_view()
add_nonogram_board = AddNonogramBoard.as_view()


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
        assert response.content.decode() == "game_turn is missing."

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

        board = await NonogramBoard.objects.aget(board_id=board_id)
        session = await Session.objects.select_related('current_game').aget(pk=session_id)

        assert response_data["board"] == board.board
        assert response_data["num_row"] == board.num_row
        assert response_data["num_column"] == board.num_column

        query_dict = {
            "session_id": session_id,
            "game_turn": -2,
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
    assert response.content.decode() == "session_id is missing."

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
    assert response.content.decode() == "board_id is missing."

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
    assert response.content.decode() == f"board_id '{BOARD_ID_UNUSED_FOR_TEST}' not found."

    query_dict = {
        "session_id": BOARD_QUERY,
        "board_id": INCORRECT_ID,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == f"board_id '{INCORRECT_ID}' is not valid id."

    query_dict = {
        "session_id": INCORRECT_ID,
        "game_turn": GAME_NOT_START,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == f"session_id '{INCORRECT_ID}' is not valid id."


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

        board_data = await NonogramBoard.objects.aget(board_id=board_id)

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
    assert response.content.decode() == "session_id is missing."

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
    assert response.content.decode() == f"session_id '{SESSION_ID_UNUSED_FOR_TEST}' not found."

    query_dict = {
        "session_id": INCORRECT_ID,
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

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == f"session_id '{INCORRECT_ID}' is not valid id."


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_create_new_session(mock_request: RequestFactory):
    url = '/create_new_session/'
    query_dict = {}
    response = await send_test_request(
        mock_request=mock_request,
        request_function=create_new_session,
        url=url,
        query_dict=query_dict,
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.content)

    session_id = response_data["session_id"]

    assert is_uuid4(session_id)
    try:
        await Session.objects.aget(pk=session_id)
    except ObjectDoesNotExist:
        assert "session_id saving failed." and False


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_create_new_game(
    mock_request: RequestFactory,
    test_sessions: List[Dict[str, Any]],
    add_test_data,
):
    url = '/create_new_game/'
    query_dict = {}
    for key, value in {
        'session_id': 1,
        'board_id': 1,
        'force_new_game': 1,
    }.items():
        response = await send_test_request(
            mock_request=mock_request,
            request_function=create_new_game,
            url=url,
            query_dict=query_dict,
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode() == f"{key} is missing."
        query_dict[key] = value

    response = await send_test_request(
        mock_request=mock_request,
        request_function=create_new_game,
        url=url,
        query_dict=query_dict,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    # assert response.content.decode() == "invalid type."

    for test_session in test_sessions:
        session_id = test_session["session_id"]
        board_id = test_session["board_id"]

        query_dict = {
            'session_id': session_id,
            'board_id': board_id,
            'force_new_game': False,
        }

        response = await send_test_request(
            mock_request=mock_request,
            request_function=create_new_game,
            url=url,
            query_dict=query_dict,
        )

        assert response.status_code == HTTPStatus.OK
        response_data = json.loads(response.content)

        assert response_data["response"] == GAME_EXIST

        query_dict = {
            'session_id': session_id,
            'board_id': board_id,
            'force_new_game': True,
        }

        response = await send_test_request(
            mock_request=mock_request,
            request_function=create_new_game,
            url=url,
            query_dict=query_dict,
        )

        assert response.status_code == HTTPStatus.OK
        response_data = json.loads(response.content)

        assert response_data["response"] == NEW_GAME_STARTED
        assert response_data["board_id"] == board_id

        query_dict = {
            'session_id': session_id,
            'board_id': RANDOM_BOARD,
            'force_new_game': True,
        }

        response = await send_test_request(
            mock_request=mock_request,
            request_function=create_new_game,
            url=url,
            query_dict=query_dict,
        )

        assert response.status_code == HTTPStatus.OK
        response_data = json.loads(response.content)

        assert response_data["response"] == NEW_GAME_STARTED
        assert response_data["board_id"] == board_id


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_create_new_game_with_new_session(
    mock_request: RequestFactory,
    test_sessions: List[Dict[str, Any]],
    add_board_test_data,
    add_new_session_test_data,
):
    url = '/create_new_game/'

    for test_session in test_sessions:
        session_id = test_session["session_id"]
        board_id = test_session["board_id"]

        query_dict = {
            'session_id': session_id,
            'board_id': board_id,
            'force_new_game': False,
        }

        response = await send_test_request(
            mock_request=mock_request,
            request_function=create_new_game,
            url=url,
            query_dict=query_dict,
        )

        assert response.status_code == HTTPStatus.OK
        response_data = json.loads(response.content)

        assert response_data["response"] == NEW_GAME_STARTED


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_add_nonogram_board(
    mock_request: RequestFactory,
):
    url = '/add_nonogram_board/'
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_image_path = os.path.join(test_data_path, 'test_board_image.jpg')
    with Image.open(test_image_path) as img:
        num_row, num_column = img.size
        byte_image = io.BytesIO()
        img.save(byte_image, format="JPEG")
        b64_image = base64.b64encode(byte_image.getvalue()).decode()

    query_dict = {
        'board': b64_image,
        'num_row': num_row,
        'num_column': num_column,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=add_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.OK

    b64_text = base64.b64encode(b"test image string").decode()

    query_dict = {
        'board': b64_text,
        'num_row': num_row,
        'num_column': num_column,
    }

    response = await send_test_request(
        mock_request=mock_request,
        request_function=add_nonogram_board,
        url=url,
        query_dict=query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
