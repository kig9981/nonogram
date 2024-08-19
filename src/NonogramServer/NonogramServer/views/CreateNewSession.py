import uuid
import json
from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from ..models import Session
from utils import is_uuid4
from utils import async_get_from_db
from utils import LogSystem
from .configure import LOG_PATH


class CreateNewSession(AsyncAPIView):
    '''
    새로운 세션을 생성하는 메서드.
    Args:
        session_id (str, optional): 유저의 session_id, 이 필드가 존재한다면 이미 존재하는 키를 찾음.
        client_session_key (str): 클라이언트측의 id. 중복 session_id 발급을 방지.
    Returns:
        요청한 사항에 대한 응답을 json형식으로 리턴.
        session_id: 생성에 성공하거나 이미 존재하는 경우 해당 session_id, 실패한 경우 0을 반환
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
        query = json.loads(request.body)
        if "client_session_key" not in query:
            return HttpResponseBadRequest("client_session_key is missing.")
        if "session_id" in query:
            return await self._get_existing_session(query["session_id"])
        client_session_key = query["client_session_key"]
        return await self._create_new_session(client_session_key)

    @logger.log
    async def _create_new_session(
        self,
        client_session_key: str,
    ) -> HttpResponse:
        try:
            session = await async_get_from_db(
                model_class=Session,
                label=f"client_session_key '{client_session_key}'",
                client_session_key=client_session_key,
            )
        except ObjectDoesNotExist:
            session_id = str(uuid.uuid4())
            session = Session(
                session_id=session_id,
                client_session_key=client_session_key,
            )
            await session.asave()
        else:
            session_id = str(session.session_id)
        response_data = {"session_id": session_id}
        return JsonResponse(response_data)

    @logger.log
    async def _get_existing_session(self, session_id: str) -> HttpResponse:
        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return await self._create_new_session()
        try:
            await async_get_from_db(
                model_class=Session,
                label=f"session_id '{session_id}'",
                session_id=session_id,
            )
        except ObjectDoesNotExist:
            return await self._create_new_session()
        response_data = {"session_id": session_id}
        return JsonResponse(response_data)
