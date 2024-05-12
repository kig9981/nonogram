import pytest
import uuid
from http import HTTPStatus
from ApiServer.views import get_nonogram_board
from ApiServer.views import get_nonogram_play
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