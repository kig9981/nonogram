import pytest
import uuid
from http import HTTPStatus
from ApiServer.views import get_nonogram_board
from ApiServer.views import get_nonogram_play
from ApiServer.views import synchronize
from ApiServer.views import make_move
from ApiServer.views import create_new_session
from ApiServer.views import create_new_game
from ..util import send_test_request


@pytest.mark.asyncio
async def test_get_nonogram_board(
    mock_request,
    mocker,
):
    url = '/get_nonogram_board/'
    mocker.patch(
        target="ApiServer.views.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "board_id": "!!!",
            "board": "!!!",
            "num_row": "!!!",
            "num_column": "!!!",
        }
    )
    response = await send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        query_dict={
            "session_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_nonogram_play(
    mock_request,
    mocker,
):
    url = '/get_nonogram_play/'
    mocker.patch(
        target="ApiServer.views.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "board": "!!!",
            "latest_turn": 0,
        }
    )
    response = await send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_play,
        url=url,
        query_dict={
            "session_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_synchronize(
    mock_request,
    mocker,
):
    url = '/synchronize/'
    mocker.patch(
        target="ApiServer.views.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "board": "!!!",
            "latest_turn": 0,
        }
    )
    response = await send_test_request(
        mock_request=mock_request,
        request_function=synchronize,
        url=url,
        query_dict={
            "session_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_make_move(
    mock_request,
    mocker,
):
    url = '/make_move/'
    mocker.patch(
        target="ApiServer.views.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "response": 0,
        }
    )
    response = await send_test_request(
        mock_request=mock_request,
        request_function=make_move,
        url=url,
        query_dict={
            "session_id": str(uuid.uuid4()),
            "x": 0,
            "y": 0,
            "state": 0,
        },
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_create_new_session(
    mock_request,
    mocker,
):
    url = '/create_new_session/'
    mocker.patch(
        target="ApiServer.views.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "session_id": "!!!",
        }
    )
    response = await send_test_request(
        mock_request=mock_request,
        request_function=create_new_session,
        url=url,
        query_dict={},
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_create_new_game(
    mock_request,
    mocker,
):
    url = '/create_new_game/'
    mocker.patch(
        target="ApiServer.views.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "response": 0,
            "board_id": "!!!",
        }
    )
    response = await send_test_request(
        mock_request=mock_request,
        request_function=create_new_game,
        url=url,
        query_dict={
            "session_id": str(uuid.uuid4()),
            "force_new_game": True,
        },
    )

    assert response.status_code == HTTPStatus.OK
