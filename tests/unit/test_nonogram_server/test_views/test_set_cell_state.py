import pytest
import json
import uuid
from typing import Any
from typing import List
from typing import Dict
from http import HTTPStatus
from NonogramServer.models import Session
from NonogramServer.views.SetCellState import SetCellState
from src.utils import async_get_from_db
from src.utils import GameBoardCellState
from Nonogram.NonogramBoard import NonogramGameplay
from django.test.client import RequestFactory
from ...util import send_test_request

SESSION_ID_UNUSED_FOR_TEST = str(uuid.uuid4())
INCORRECT_ID = "xxxxxxx"

set_cell_state = SetCellState.as_view()

def get_url(session_id):
    return f"/set_cell_state/{session_id}/move/"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_session_for_set_cell_state(
    mock_request: RequestFactory,
    test_sessions: List[Dict[str, Any]],
    add_test_data,
):
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

        session = await async_get_from_db(
            model_class=Session,
            label=f"session_id '{session_id}'",
            select_related=['board_data', 'current_game'],
            session_id=session_id,
        )
        play = NonogramGameplay(
            data=session,
            db_sync=False,
        )

        for x in range(play.num_row):
            for y in range(play.num_column):
                for new_state in moves:
                    expected_result = play.mark(x, y, new_state)
                    query_dict = {
                        "x_coord": x,
                        "y_coord": y,
                        "new_state": new_state,
                    }

                    response = await send_test_request(
                        method_type="POST",
                        mock_request=mock_request,
                        request_function=set_cell_state,
                        url=get_url(session_id),
                        query_dict=query_dict,
                        session_id=session_id,
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
    query_dict = {}

    response = await send_test_request(
        method_type="POST",
        mock_request=mock_request,
        request_function=set_cell_state,
        url=get_url('1'),
        query_dict=query_dict,
        session_id='1',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == "x_coord is missing."

    query_dict = {
        "session_id": SESSION_ID_UNUSED_FOR_TEST,
        "x_coord": 0,
        "y_coord": 0,
        "new_state": GameBoardCellState.NOT_SELECTED,
    }

    response = await send_test_request(
        method_type="POST",
        mock_request=mock_request,
        request_function=set_cell_state,
        url=get_url(SESSION_ID_UNUSED_FOR_TEST),
        query_dict=query_dict,
        session_id=SESSION_ID_UNUSED_FOR_TEST,
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
        method_type="POST",
        mock_request=mock_request,
        request_function=set_cell_state,
        url=get_url(INCORRECT_ID),
        query_dict=query_dict,
        session_id=INCORRECT_ID,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == f"session_id '{INCORRECT_ID}' is not valid id."
