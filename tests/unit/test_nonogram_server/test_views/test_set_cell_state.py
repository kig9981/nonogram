import pytest
import json
import uuid
from typing import Any
from typing import List
from typing import Dict
from http import HTTPStatus
from NonogramServer.models import NonogramBoard
from NonogramServer.models import Session
from NonogramServer.views.SetCellState import SetCellState
from src.utils import GameBoardCellState
from src.utils import deserialize_gameboard
from src.utils import deserialize_gameplay
from Nonogram.NonogramBoard import NonogramGameplay
from Nonogram.RealGameBoard import RealGameBoard
from django.test.client import RequestFactory
from ...util import send_test_request

SESSION_ID_UNUSED_FOR_TEST = str(uuid.uuid4())
INCORRECT_ID = "xxxxxxx"

set_cell_state = SetCellState.as_view()


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
