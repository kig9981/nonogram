import pytest
import json
from typing import Any
from typing import List
from typing import Dict
from http import HTTPStatus
from NonogramServer.views.GetNonogramBoard import GetNonogramBoard
from django.test.client import RequestFactory
from ...util import send_test_request
from ...util import TestConfig


get_nonogram_board = GetNonogramBoard.as_view()


def get_url(board_id):
    return f"/nonogram/{board_id}/"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_board_for_get_nonogram_board(
    mock_request: RequestFactory,
    test_boards: List[Dict[str, Any]],
    add_test_data,
):
    for test_board in test_boards:
        query_dict = {
            "board_id": test_board['board_id'],
        }
        response = await send_test_request(
            method_type="GET",
            mock_request=mock_request,
            request_function=get_nonogram_board,
            url=get_url(**query_dict),
            **query_dict,
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
    query_dict = {
        "board_id": TestConfig.BOARD_ID_UNUSED_FOR_TEST,
    }

    response = await send_test_request(
        method_type="GET",
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=get_url(**query_dict),
        **query_dict,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.content.decode() == f"board_id '{TestConfig.BOARD_ID_UNUSED_FOR_TEST}' not found."

    query_dict = {
        "board_id": TestConfig.INCORRECT_ID,
    }

    response = await send_test_request(
        method_type="GET",
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=get_url(**query_dict),
        **query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == f"board_id '{TestConfig.INCORRECT_ID}' is not valid id."
