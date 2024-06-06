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


class GetNonogramPlay(AsyncAPIView):
    '''
    진행중인 세션의 노노그램 보드 게임 현황에 대한 정보를 반환하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id

    Returns:
        해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        진행중인 게임이 없으면 404에러(board not found)를 반환.
        존재한다면 게임 진행 상황을 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        board (list[list]): 가장 최근 움직임까지 게임 진행 정보를 반영한 게임보드를 2차원 배열로 반환.
                            게임 진행중이 아니라면 빈 배열 반환.
                            각 원소의 값은 Nonogram.utils의 GameBoardCellState, RealBoardCellState 참조.
        latest_turn (int): 가장 최근 턴 수를 반환.
    '''
    async def get(
        self,
        request: HttpRequest,
        session_id: str,
    ) -> HttpResponse:
        LATEST_TURN = -1

        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"'{session_id}' is not valid id.")

        url = f"{NONOGRAM_SERVER_URL}/sessions/{session_id}/turn/{LATEST_TURN}"
        response = await send_request(
            method_type="GET",
            url=url,
        )
        status_code = response["status_code"]

        if status_code == HTTPStatus.OK:
            response_data = {
                "board": response["board"],
                "latest_turn": response["latest_turn"],
            }
            return JsonResponse(response_data)

        elif status_code == HTTPStatus.NOT_FOUND:
            return HttpResponseNotFound(response["response"])
        else:
            return HttpResponseServerError("unknown error")
