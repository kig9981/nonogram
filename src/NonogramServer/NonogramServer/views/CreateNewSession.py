import uuid
from django.views import View
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from ..models import Session


class CreateNewSession(View):
    '''
    새로운 세션을 생성하는 메서드.
    Args:
        None
    Returns:
        요청한 사항에 대한 응답을 json형식으로 리턴.
        session_id: 생성에 성공한 경우 해당 session_id, 실패한 경우 0을 반환
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
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id)
        await session.asave()
        response_data = {"session_id": session_id}
        return JsonResponse(response_data)
