import pytest
import json
from http import HTTPStatus
from ApiServer.views import get_nonogram_board
from django.test.client import RequestFactory
from django.http import HttpRequest
from django.http import HttpResponse
from typing import Callable
from typing import Dict
from typing import Any


@pytest.fixture
def mock_request():
    return RequestFactory()


async def send_test_request(
    mock_request: RequestFactory,
    request_function: Callable[[HttpRequest], HttpResponse],
    url: str,
    query_dict: Dict[str, Any],
) -> HttpResponse:
    query = json.dumps(query_dict)
    request = mock_request.post(
        path=url,
        data=query,
        content_type="Application/json",
    )
    response = await request_function(request)

    return response


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
