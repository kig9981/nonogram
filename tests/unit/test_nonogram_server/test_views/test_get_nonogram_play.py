import pytest
import json
from typing import Any
from typing import List
from typing import Dict
from http import HTTPStatus
from NonogramServer.models import Session
from NonogramServer.views.GetNonogramPlay import GetNonogramPlay
from django.test.client import RequestFactory
from ...util import send_test_request
from ...util import TestConfig


get_nonogram_play = GetNonogramPlay.as_view()


def get_url(session_id, game_turn_str):
    return f'/sessions/{session_id}/turn/{game_turn_str}/'


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_session_for_get_nonogram_play(
    mock_request: RequestFactory,
    test_sessions: List[Dict[str, Any]],
    add_test_data,
):
    for test_session in test_sessions:
        session_id = test_session["session_id"]

        query_dict = {
            "session_id": session_id,
            "game_turn_str": str(TestConfig.INVALID_GAME_TURN),
        }
        response = await send_test_request(
            method_type="GET",
            mock_request=mock_request,
            request_function=get_nonogram_play,
            url=get_url(**query_dict),
            **query_dict,
        )

        session = await Session.objects.select_related('current_game').aget(pk=session_id)
        latest_turn = 0 if session.current_game is None else session.current_game.current_turn

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode() == f"invalid game_turn. must be between 0 to {latest_turn}(latest turn)"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_history_for_get_nonogram_play(
    mock_request: RequestFactory,
    test_histories: List[Dict[str, Any]],
    add_test_data,
):
    for test_history in test_histories:
        session_id = test_history["session_id"]
        for cur_turn, move in enumerate(test_history["moves"]):
            query_dict = {
                "session_id": session_id,
                "game_turn_str": str(cur_turn + 1),
            }
            response = await send_test_request(
                method_type="GET",
                mock_request=mock_request,
                request_function=get_nonogram_play,
                url=get_url(**query_dict),
                **query_dict,
            )

            assert response.status_code == HTTPStatus.OK

            applied_board = move["board"]
            response_data = json.loads(response.content)

            assert response_data["board"] == applied_board


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_nonogram_play(
    mock_request: RequestFactory,
    add_test_data,
):
    query_dict = {
        "session_id": TestConfig.INCORRECT_ID,
        "game_turn_str": str(TestConfig.GAME_NOT_START),
    }

    response = await send_test_request(
        method_type="GET",
        mock_request=mock_request,
        request_function=get_nonogram_play,
        url=get_url(**query_dict),
        **query_dict,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.decode() == f"session_id '{TestConfig.INCORRECT_ID}' is not valid id."
