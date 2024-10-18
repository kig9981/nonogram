import json
from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from Nonogram.NonogramBoard import NonogramGameplay
from ..models import Game
from http import HTTPStatus
from utils import async_get_from_db
from utils import is_uuid4
from utils import LogSystem
from utils import Config
from utils import LockManager
from .configure import LOG_PATH


class SetCellState(AsyncAPIView):
    '''
    진행중인 게임의 특정 cell의 상태를 변화시키는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id
        x_coord (int): 변화시키는 x좌표
        y_coord (int): 변화시키는 y좌표
        new_state (int): 변화시킬 상태, Nonogram.utils.GameBoardCellState 참고
    Returns:
        해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        현재 진행중인 게임이 없다면 404에러(gameplay not found)를 반환.
        좌표가 유효하지 않을 경우 400에러(invalid coordinate)를 반환.
        상태가 유효하지 않을 경우 400에러(invalid state)를 반환.
        이외의 경우에는 결과를 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        response (int): 적용 여부에 따라 응답 코드를 반환.
                        0=UNCHANGED
                        1=APPLIED
                        2=GAME_OVER
    '''
    logger = LogSystem(
        module_name=__name__,
        log_path=LOG_PATH,
    )

    @logger.log
    async def post(
        self,
        request: HttpRequest,
        session_id: str,
    ) -> HttpResponse:
        if request.content_type != "application/json":
            return HttpResponseBadRequest("Must be Application/json request.")
        query = json.loads(request.body)
        if 'moves' not in query:
            return HttpResponseBadRequest("moves are missing.")
        
        moves = query['moves']

        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"session_id '{session_id}' is not valid id.")
        
        if not isinstance(moves, list):
            return HttpResponseBadRequest(f"Invalid moves list.")

        async with LockManager(lock_key=f"set_cell_state:{session_id}", max_retries=0, retry_interval=0.1) as lock_result:
            if not lock_result:
                return HttpResponse("Too many requests. Try again.", status=HTTPStatus.TOO_MANY_REQUESTS)
            try:
                current_game = await async_get_from_db(
                    model_class=Game,
                    label="",
                    select_related=["current_session", "board_data"],
                    current_session__session_id=session_id,
                    active=True,
                )
            except ObjectDoesNotExist:
                return HttpResponseNotFound("gameplay not found.")

            gameplay = NonogramGameplay(
                data=current_game,
            )
            num_row = gameplay.num_row
            num_column = gameplay.num_column

            for elem in moves:
                if (
                    not isinstance(elem, list) or
                    len(elem) != 3
                ):
                    return HttpResponseBadRequest(f"Invalid moves list.")
                x, y, new_state = elem
                if not isinstance(x, int) or not isinstance(y, int) or not (0 <= x < num_row) or not (0 <= y < num_column):
                    return HttpResponseBadRequest("Invalid coordinate.")
                if not isinstance(new_state, int) or not (Config.GAME_BOARD_CELL_STATE_LOWERBOUND <= new_state <= Config.GAME_BOARD_CELL_STATE_UPPERBOUND):
                    return HttpResponseBadRequest("Invalid state. Either 0(NOT_SELECTED), 1(REVEALED), 2(MARK_X), 3(MARK_QUESTION), or 4(MARK_WRONG).")
                changed = await gameplay.async_mark(x, y, new_state)

            response_data = {"response": changed}
            return JsonResponse(response_data)
