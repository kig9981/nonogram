import pytest
from typing import Any
from typing import List
from typing import Dict
from http import HTTPStatus
from NonogramServer.views.HandleGame import HandleGame
from django.test.client import RequestFactory
from ...util import send_test_request
from ...util import TestConfig


get_session_board = HandleGame.as_view()


def get_url(session_id):
    return f"/nonogram/{session_id}/"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_session_board(
    mock_request: RequestFactory,
    test_sessions: List[Dict[str, Any]],
    add_test_data,
):
    query_dict = {
        "session_id": TestConfig.SESSION_ID_UNUSED_FOR_TEST,
    }

    response = await send_test_request(
        method_type="GET",
        mock_request=mock_request,
        request_function=get_session_board,
        url=get_url(**query_dict),
        **query_dict,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.content.decode() == f"session_id '{TestConfig.SESSION_ID_UNUSED_FOR_TEST}' not found."

    query_dict = {
        "session_id": TestConfig.INCORRECT_ID,
    }

    response = await send_test_request(
        method_type="GET",
        mock_request=mock_request,
        request_function=get_session_board,
        url=get_url(**query_dict),
        **query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == f"session_id '{TestConfig.INCORRECT_ID}' is not valid id."

    for test_session in test_sessions:
        session_id = test_session["session_id"]

        query_dict = {
            "session_id": session_id,
        }

        response = await send_test_request(
            method_type="GET",
            mock_request=mock_request,
            request_function=get_session_board,
            url=get_url(**query_dict),
            **query_dict,
        )

        assert response.status_code == HTTPStatus.OK
