import pytest
import json
from django.test.client import RequestFactory
from django.http import HttpRequest
from django.http import HttpResponse
from typing import Callable
from typing import Dict
from typing import Any


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