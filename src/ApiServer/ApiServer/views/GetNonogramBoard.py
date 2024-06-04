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


class GetNonogramBoard(AsyncAPIView):
    '''
    진행중인 세션의 노노그램 보드에 대한 정보를 반환하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id

    Returns:
        해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        존재하는데 게임 진행중이 아니라면 404에러(board not found)를 반환.
        게임 진행중이라면 board_id와 게임 보드 정보를 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        board_id (str): board_id정보를 uuid형식으로 반환
        board (list[list]): 게임보드를 2차원 배열로 반환.
                            각 원소의 값은 Nonogram.utils의 GameBoardCellState, RealBoardCellState 참조.
        num_row (int): 게임보드의 행 수
        num_column (int): 게임보드의 열 수
    '''
    async def get(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        GAMEBOARD_QUERY = 0
        session_id = kwargs["session_id"]

        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"'{session_id}' is not valid id.")

        url = f"{NONOGRAM_SERVER_URL}/get_nonogram_server"
        query_dict = {
            "session_id": session_id,
            "game_turn": GAMEBOARD_QUERY,
        }
        response = await send_request(
            url=url,
            request=query_dict,
        )
        status_code = response["status_code"]

        if status_code == HTTPStatus.OK:
            response_data = {
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
