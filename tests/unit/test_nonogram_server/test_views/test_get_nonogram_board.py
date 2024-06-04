import pytest
import json
import uuid
from typing import Any
from typing import List
from typing import Dict
from http import HTTPStatus
from NonogramServer.models import NonogramBoard
from NonogramServer.models import Session
from NonogramServer.views.GetNonogramBoard import GetNonogramBoard
from django.test.client import RequestFactory
from ...util import send_test_request

BOARD_ID_UNUSED_FOR_TEST = str(uuid.uuid4())
INCORRECT_ID = "xxxxxxx"
BOARD_QUERY = 0
GAME_NOT_START = 0
INVALID_GAME_TURN = -2

get_nonogram_board = GetNonogramBoard.as_view()


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
