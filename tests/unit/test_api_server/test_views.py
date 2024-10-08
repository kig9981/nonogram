import pytest
import uuid
from http import HTTPStatus
from ApiServer.views.GetNonogramBoard import GetNonogramBoard
from ApiServer.views.GetNonogramPlay import GetNonogramPlay
from ApiServer.views.Synchronize import Synchronize
from ApiServer.views.MakeMove import MakeMove
from ApiServer.views.CreateNewSession import CreateNewSession
from ApiServer.views.CreateNewGame import CreateNewGame
from ..util import send_test_request


get_nonogram_board = GetNonogramBoard.as_view()
get_nonogram_play = GetNonogramPlay.as_view()
synchronize = Synchronize.as_view()
make_move = MakeMove.as_view()
create_new_session = CreateNewSession.as_view()
create_new_game = CreateNewGame.as_view()
session_id = str(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_nonogram_board(
    mock_request,
    mocker,
):
    url = f'/sessions/{session_id}/board/'
    mocker.patch(
        target="ApiServer.views.GetNonogramBoard.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "board_id": "!!!",
            "board": "!!!",
            "num_row": "!!!",
            "num_column": "!!!",
        }
    )
    response = await send_test_request(
        method_type="GET",
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        session_id=session_id,
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_nonogram_play(
    mock_request,
    mocker,
):
    url = f'/sessions/{session_id}/play/'
    mocker.patch(
        target="ApiServer.views.GetNonogramPlay.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "board": "!!!",
            "latest_turn": 0,
        }
    )
    response = await send_test_request(
        method_type="GET",
        mock_request=mock_request,
        request_function=get_nonogram_play,
        url=url,
        session_id=session_id,
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_synchronize(
    mock_request,
    mocker,
):
    url = f'/sessions/{session_id}/sync/{0}'
    mocker.patch(
        target="ApiServer.views.Synchronize.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "board": "!!!",
            "latest_turn": 0,
        }
    )
    response = await send_test_request(
        method_type="GET",
        mock_request=mock_request,
        request_function=synchronize,
        url=url,
        session_id=session_id,
        game_turn=0,
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_make_move(
    mock_request,
    mocker,
):
    url = f'/sessions/{session_id}/move/'
    mocker.patch(
        target="ApiServer.views.MakeMove.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "response": 0,
        }
    )
    response = await send_test_request(
        method_type="POST",
        mock_request=mock_request,
        request_function=make_move,
        url=url,
        query_dict={
            "x": 0,
            "y": 0,
            "state": 0,
        },
        session_id=session_id,
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_create_new_session(
    mock_request,
    mocker,
):
    url = '/sessions/'
    mocker.patch(
        target="ApiServer.views.CreateNewSession.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "session_id": "!!!",
        }
    )
    response = await send_test_request(
        method_type="POST",
        mock_request=mock_request,
        request_function=create_new_session,
        url=url,
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_create_new_game(
    mock_request,
    mocker,
):
    url = f'/sessions/{session_id}/'
    mocker.patch(
        target="ApiServer.views.CreateNewGame.send_request",
        return_value={
            "status_code": HTTPStatus.OK,
            "response": 0,
            "board_id": "!!!",
            "board": [[0, 1], [1, 0]],
            "num_row": 2,
            "num_column": 2,
        }
    )
    response = await send_test_request(
        method_type="POST",
        mock_request=mock_request,
        request_function=create_new_game,
        url=url,
        query_dict={
            "board_id": str(uuid.uuid4()),
        },
        session_id=session_id,
    )

    assert response.status_code == HTTPStatus.OK
