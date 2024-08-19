import pytest
import json
from http import HTTPStatus
from NonogramServer.models import Session
from NonogramServer.views.CreateNewSession import CreateNewSession
from src.utils import is_uuid4
from django.core.exceptions import ObjectDoesNotExist
from django.test.client import RequestFactory
from ...util import send_test_request

create_new_session = CreateNewSession.as_view()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_create_new_session(mock_request: RequestFactory):
    url = '/sessions/'
    query_dict = {
        "client_session_key": "0.0.0.0_test-agent"
    }
    response = await send_test_request(
        method_type="POST",
        mock_request=mock_request,
        request_function=create_new_session,
        url=url,
        query_dict=query_dict,
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.content)

    session_id = response_data["session_id"]

    assert is_uuid4(session_id)
    try:
        await Session.objects.aget(pk=session_id)
    except ObjectDoesNotExist:
        assert "session_id saving failed." and False
