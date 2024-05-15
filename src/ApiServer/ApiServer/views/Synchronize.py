import json
from .configure import NONOGRAM_SERVER_URL
from django.views import View
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from utils import is_uuid4
from utils import send_request
from utils import convert_board_to_hash
from http import HTTPStatus


class Synchronize(View):
    '''
    진행중인 세션의 노노그램 보드 게임 진행을 동기화하기 위한 메서드. 진행중인 턴을 바탕으로 동기화한다.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id
        game_turn (int): 현재 진행 중인 턴수

    Returns:
        해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        진행중인 게임이 없으면 404에러(board not found)를 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        hash (str): invalid한 턴수인 경우에만 채워지는 필드. 게임 진행 정보를 반환.
                            각 원소의 값은 Nonogram.utils의 GameBoardCellState, RealBoardCellState 참조.
        latest_turn (int): 가장 최근 턴 수를 반환.
    '''
    async def get(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        return HttpResponse("synchronize(get)")

    async def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        LATEST_TURN = -1

        if request.content_type != "application/json":
            return HttpResponseBadRequest("Must be Application/json request.")

        query = json.loads(request.body)

        if "session_id" not in query:
            return HttpResponseBadRequest("session_id is missing.")

        session_id = query["session_id"]

        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"'{session_id}' is not valid id.")

        url = f"{NONOGRAM_SERVER_URL}/get_nonogram_server"
        query_dict = {
            "session_id": session_id,
            "game_turn": LATEST_TURN,
        }
        response = await send_request(
            url=url,
            request=query_dict,
        )
        status_code = response["status_code"]

        if status_code == HTTPStatus.OK:
            response_data = {
                "hash": convert_board_to_hash(response["board"]),
                "latest_turn": response["latest_turn"],
            }
            return JsonResponse(response_data)

        elif status_code == HTTPStatus.NOT_FOUND:
            return HttpResponseNotFound(response["response"])
        else:
            return HttpResponseServerError("unknown error")