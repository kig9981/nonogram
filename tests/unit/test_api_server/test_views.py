import pytest
from http import HTTPStatus
from ApiServer.views import get_nonogram_board
from ..util import send_test_request


@pytest.mark.asyncio
async def test_get_nonogram_board(mock_request):
    url = '/get_nonogram_board/'
    response = await send_test_request(
        mock_request=mock_request,
        request_function=get_nonogram_board,
        url=url,
        query_dict={},
    )

    assert response.status_code == HTTPStatus.OK
