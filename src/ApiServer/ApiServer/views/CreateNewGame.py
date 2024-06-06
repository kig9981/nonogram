import json
from .configure import NONOGRAM_SERVER_URL
from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from utils import is_uuid4
from utils import send_request
from http import HTTPStatus


class CreateNewGame(AsyncAPIView):
    '''
    세션에서 새 게임을 시작하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id
        board_id (str): 시작하려고 하는 board_id, 없을 경우 랜덤 보드로 시작
        force_new_game (bool): 이미 진행중인 게임을 강제로 종료 후 시작할지 여부
    Returns:
        해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        존재한다면 board_id와 게임 보드 정보를 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        response (int): 적용 여부에 따라 응답 코드를 반환.
                        0=GAME_EXIST
                        1=NEW_GAME_STARTED
        board_id (str): 새로 시작한 board_id정보를 uuid형식으로 반환.
    '''

    async def post(
        self,
        request: HttpRequest,
        session_id: str,
    ) -> HttpResponse:
        return await self._create_new_game(
            request=request,
            session_id=session_id,
            force_new_game=False,
        )
    
    async def put(
        self,
        request: HttpRequest,
        session_id: str,
    ) -> HttpResponse:
        return await self._create_new_game(
            request=request,
            session_id=session_id,
            force_new_game=True,
        )
        
    async def _create_new_game(
        self,
        request: HttpRequest,
        session_id: str,
        force_new_game: bool,
    ) -> HttpResponse:
        RANDOM_BOARD = 0
        if request.content_type != "application/json":
            return HttpResponseBadRequest("Must be Application/json request.")

        query = json.loads(request.body)

        board_id = query["board_id"] if "board_id" in query else RANDOM_BOARD

        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"session_id '{session_id}' is not valid id.")
        if board_id != RANDOM_BOARD and (not isinstance(board_id, str) or not is_uuid4(board_id)):
            return HttpResponseBadRequest(f"board_id '{board_id}' is not valid id.")

        url = f"{NONOGRAM_SERVER_URL}/sessions/{session_id}"
        query_dict = {
            "board_id": board_id,
        }
        response = await send_request(
            method_type="PUT" if force_new_game else "POST",
            url=url,
            request=query_dict,
        )
        status_code = response["status_code"]

        if status_code == HTTPStatus.OK:
            response_data = {
                "response": response["response"],
                "board_id": response["board_id"],
                "board": response["board"],
                "num_row": response["num_row"],
                "num_column": response["num_column"],
            }
            return JsonResponse(response_data)

        elif status_code == HTTPStatus.NOT_FOUND:
            return HttpResponseNotFound(response["response"])
        else:
            return HttpResponseServerError("unknown error")

