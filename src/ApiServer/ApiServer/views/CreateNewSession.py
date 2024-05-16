from .configure import NONOGRAM_SERVER_URL
from django.views import View
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseServerError
from utils import send_request
from http import HTTPStatus


class CreateNewSession(View):
    '''
    새 세션을 생성하는 메서드.
    Args:

    Returns:
        만들어진 session id를 반환

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        session_id (str): session_id를 uuid형식으로 반환.
    '''
    async def get(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        return HttpResponse("create_new_session(get)")

    async def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        # TODO: 비정상적인 쿼리에 대한 거부(같은 ip에 대해서 쿨타임 설정)
        url = f"{NONOGRAM_SERVER_URL}/create_new_session"
        response = await send_request(
            url=url,
            request={},
        )
        status_code = response["status_code"]

        if status_code == HTTPStatus.OK:
            response_data = {
                "session_id": response["session_id"],
            }
            return JsonResponse(response_data)
        else:
            return HttpResponseServerError("unknown error")
