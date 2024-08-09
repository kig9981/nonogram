import json
from .configure import NONOGRAM_SERVER_URL
from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseServerError
from utils import send_request
from utils import LogSystem
from .configure import LOG_PATH
from http import HTTPStatus


class CreateNewSession(AsyncAPIView):
    '''
    새 세션을 생성하는 메서드.
    Args:

    Returns:
        만들어진 session id를 반환

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        session_id (str): session_id를 uuid형식으로 반환.
    '''
    logger = LogSystem(
        module_name=__name__,
        log_path=LOG_PATH,
    )

    @logger.log
    async def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        # TODO: 비정상적인 쿼리에 대한 거부(같은 ip에 대해서 쿨타임 설정)
        query = {}

        if request.content_type == "application/json":
            query = json.loads(request.body)

        url = f"{NONOGRAM_SERVER_URL}/sessions"
        response = await send_request(
            method_type="POST",
            url=url,
            request=query,
        )
        status_code = response["status_code"]

        if status_code == HTTPStatus.OK:
            response_data = {
                "session_id": response["session_id"],
            }
            return JsonResponse(response_data)
        else:
            return HttpResponseServerError("unknown error")
