import uuid
import json
from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from ..models import Session
from utils import is_uuid4
from utils import async_get_from_db


class CreateNewSession(AsyncAPIView):
    '''
    새로운 세션을 생성하는 메서드.
    Args:
        None
    Returns:
        요청한 사항에 대한 응답을 json형식으로 리턴.
        session_id: 생성에 성공한 경우 해당 session_id, 실패한 경우 0을 반환
    '''
    async def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        if request.content_type == "application/json":
            query = json.loads(request.body)
            if "session_id" in query:
                return await self._get_existing_session(query["session_id"])
        return await self._create_new_session()

    async def _create_new_session(self) -> HttpResponse:
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id)
        await session.asave()
        response_data = {"session_id": session_id}
        return JsonResponse(response_data)

    async def _get_existing_session(self, session_id: str) -> HttpResponse:
        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return self._create_new_session()
        try:
            session = await async_get_from_db(
                model_class=Session,
                label=f"session_id '{session_id}'",
                session_id=session_id,
            )
        except ObjectDoesNotExist as error:
            return self._create_new_session()
        response_data = {"session_id": session_id}
        return JsonResponse(response_data)
