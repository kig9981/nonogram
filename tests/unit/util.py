import json
from django.test.client import RequestFactory
from django.http import HttpRequest
from django.http import HttpResponse
from typing import Callable
from typing import Dict
from typing import Any


async def send_test_request(
    method_type: str,
    mock_request: RequestFactory,
    request_function: Callable[[HttpRequest], HttpResponse],
    url: str,
    query_dict: Dict[str, Any] = {},
    **kwargs,
) -> HttpResponse:
    if method_type == "POST":
        query = json.dumps(query_dict)
        request = mock_request.post(
            path=url,
            data=query,
            content_type="application/json",
            HTTP_X_FORWARDED_FOR='0.0.0.0',
            HTTP_USER_AGENT='test-agent',
        )
        response = await request_function(request, **kwargs)
    elif method_type == "GET":
        request = mock_request.get(
            url,
            HTTP_X_FORWARDED_FOR='0.0.0.0',
            HTTP_USER_AGENT='test-agent',
        )
        response = await request_function(request, **kwargs)
    elif method_type == "PUT":
        query = json.dumps(query_dict)
        request = mock_request.put(
            path=url,
            data=query,
            content_type="application/json",
            HTTP_X_FORWARDED_FOR='0.0.0.0',
            HTTP_USER_AGENT='test-agent',
        )
        response = await request_function(request, **kwargs)
    else:
        raise Exception("Invalid method type")

    return response
