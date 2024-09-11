import pytest
import json
from typing import Any
from typing import List
from typing import Dict
from http import HTTPStatus
from NonogramServer.views.HandleGame import HandleGame
from django.test.client import RequestFactory
from ...util import send_test_request
from src.utils import is_uuid4
from src.utils import Config


create_new_game = HandleGame.as_view()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_create_new_game(
    mock_request: RequestFactory,
    test_games: List[Dict[str, Any]],
    add_test_data,
):
    url = '/sessions/'
    query_dict = {}
    for key, value in {
        'board_id': 1,
    }.items():
        response = await send_test_request(
            method_type="POST",
            mock_request=mock_request,
            request_function=create_new_game,
            url=f"{url}/1/",
            query_dict=query_dict,
            session_id="1",
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode() == f"{key} is missing."
        query_dict[key] = value

    response = await send_test_request(
        method_type="POST",
        mock_request=mock_request,
        request_function=create_new_game,
        url=f"{url}/1/",
        query_dict=query_dict,
        session_id="1",
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    # assert response.content.decode() == "invalid type."

    for test_game in test_games:
        session_id = test_game["session_id"]
        board_id = test_game["board_id"]

        query_dict = {
            'board_id': board_id,
        }

        response = await send_test_request(
            method_type="POST",
            mock_request=mock_request,
            request_function=create_new_game,
            url=f"{url}/{session_id}/",
            query_dict=query_dict,
            session_id=session_id,
        )

        assert response.status_code == HTTPStatus.OK
        response_data = json.loads(response.content)

        assert response_data["response"] == Config.GAME_EXIST

        response = await send_test_request(
            method_type="PUT",
            mock_request=mock_request,
            request_function=create_new_game,
            url=f"{url}/{session_id}/",
            query_dict=query_dict,
            session_id=session_id,
        )

        assert response.status_code == HTTPStatus.OK
        response_data = json.loads(response.content)

        assert response_data["response"] == Config.NEW_GAME_STARTED
        assert response_data["board_id"] == board_id

        query_dict = {
            'board_id': Config.RANDOM_BOARD,
        }

        response = await send_test_request(
            method_type="PUT",
            mock_request=mock_request,
            request_function=create_new_game,
            url=f"{url}/{session_id}/",
            query_dict=query_dict,
            session_id=session_id,
        )

        assert response.status_code == HTTPStatus.OK
        response_data = json.loads(response.content)

        assert response_data["response"] == Config.NEW_GAME_STARTED
        assert is_uuid4(response_data["board_id"])
