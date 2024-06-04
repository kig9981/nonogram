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


class MakeMove(AsyncAPIView):
    '''
    게임이 진행중인 세션에서 노노그램 보드에 입력을 처리하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id
        x (int): 행 정보
        y (int): 열 정보
        state (int): 바꾸려고 하는 상태 정보

    Returns:
        해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        x와 y가 게임보드 범위를 벗어난다면 400에러(invalid coordinate)를 반환.
        상태가 유효하지 않다면 400에러(invalid state)를 반환.
        존재한다면 결과를 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        result (int): 해당 입력에 대한 처리 결과를 반환
                      0: 변화 없음
                      1: 정상적으로 반영됨
                      2: 해당 움직임으로 게임 종료(게임이 종료된 이후의 모든 요청은 이 답으로 돌아감)
    '''
    async def post(
        self,
        request: HttpRequest,
        session_id: str,
    ) -> HttpResponse:
        if request.content_type != "application/json":
            return HttpResponseBadRequest("Must be Application/json request.")

        query = json.loads(request.body)

        if "x" not in query:
            return HttpResponseBadRequest("x is missing.")
        if "y" not in query:
            return HttpResponseBadRequest("y is missing.")
        if "state" not in query:
            return HttpResponseBadRequest("state is missing.")

        x = query["x"]
        y = query["y"]
        state = query["state"]

        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"'{session_id}' is not valid id.")
        if not isinstance(x, int) or not isinstance(y, int):
            return HttpResponseBadRequest("Invalid coordinate(type must be integer)")
        if not isinstance(state, int) or not (0 <= state <= 3):
            return HttpResponseBadRequest("Invalid state(type must be integer)")

        url = f"{NONOGRAM_SERVER_URL}/set_cell_state"
        query_dict = {
            "session_id": session_id,
            "x_coord": x,
            "y_coord": y,
            "new_state": state,
        }
        response = await send_request(
            url=url,
            request=query_dict,
        )
        status_code = response["status_code"]

        if status_code == HTTPStatus.OK:
            response_data = {
                "response": response["response"],
            }
            return JsonResponse(response_data)

        elif status_code == HTTPStatus.BAD_REQUEST:
            return HttpResponseBadRequest(response["response"])
        elif status_code == HTTPStatus.NOT_FOUND:
            return HttpResponseNotFound(response["response"])
        else:
            return HttpResponseServerError("unknown error")
