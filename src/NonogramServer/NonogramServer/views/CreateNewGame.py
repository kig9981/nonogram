import json
import asyncio
from django.views import View
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from ..models import NonogramBoard
from ..models import Session
from ..models import History
from utils import GameBoardCellState
from utils import async_get_from_db
from utils import serialize_gameboard
from utils import is_uuid4


class CreateNewGame(View):
    '''
    특정 세션에서 새 게임을 시작하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id
        board_id (str): 시작하려고 하는 board_id, 0일 경우 랜덤 보드로 시작
        force_new_game (bool): 이미 진행중인 게임을 강제로 종료 후 시작할지 여부
    Returns:
        요청한 사항에 대한 응답을 json형식으로 리턴.

        response (int): 적용 여부에 따라 응답 코드를 반환.
                        0=GAME_EXIST
                        1=NEW_GAME_STARTED
        board_id (str): 랜덤 보드를 요청한 경우 선택된 보드를, 아니면 argument로 주어진 board_id를 반환
    '''
    async def get(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        return HttpResponse("create_new_game(get)")

    async def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        RANDOM_BOARD = 0
        GAME_EXIST = 0
        NEW_GAME_STARTED = 1
        if request.content_type != "application/json":
            return HttpResponseBadRequest("Must be Application/json request.")
        query = json.loads(request.body)
        if 'session_id' not in query:
            return HttpResponseBadRequest("session_id is missing.")
        if 'board_id' not in query:
            return HttpResponseBadRequest("board_id is missing.")
        if 'force_new_game' not in query:
            return HttpResponseBadRequest("force_new_game is missing.")

        session_id = query['session_id']
        board_id = query['board_id']
        force_new_game = query['force_new_game']

        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"session_id '{session_id}' is not valid id.")
        if board_id != RANDOM_BOARD and (not isinstance(board_id, str) or not is_uuid4(board_id)):
            return HttpResponseBadRequest(f"board_id '{board_id}' is not valid id.")
        if not isinstance(force_new_game, bool):
            return HttpResponseBadRequest("force_new_game not valid.")

        try:
            session = await async_get_from_db(
                model_class=Session,
                label=f"session_id '{session_id}'",
                select_related=['current_game', 'board_data'],
                session_id=session_id,
            )
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")

        coroutine = []

        if session.board_data is not None:
            if not force_new_game:
                response_data = {
                    "response": GAME_EXIST,
                }
                return JsonResponse(response_data)

            # TODO: 비동기 task queue를 사용해서 업데이트하는 로직으로 변경

            async for history in History.objects.filter(current_session=session):
                history.current_session = None
                coroutine.append(asyncio.create_task(history.asave()))

        if board_id == RANDOM_BOARD:
            # TODO: 더 빠르게 랜덤셀렉트하는걸로 바꾸기
            board_data = await NonogramBoard.objects.order_by('?').afirst()
            board_id = str(board_data.board_id)
        else:
            try:
                board_data = await async_get_from_db(
                    model_class=NonogramBoard,
                    label=f"board_id '{board_id}'",
                    board_id=board_id,
                )
            except ObjectDoesNotExist as error:
                return HttpResponseNotFound(f"{error} not found.")

        session.board_data = board_data
        session.board = serialize_gameboard(
            [
                [GameBoardCellState.NOT_SELECTED for _ in range(board_data.num_column)]
                for _ in range(board_data.num_row)
            ]
        )
        session.current_game = None
        session.unrevealed_counter = board_data.black_counter

        coroutine.append(asyncio.create_task(session.asave()))

        response_data = {
            "response": NEW_GAME_STARTED,
            "board_id": board_id,
        }

        await asyncio.gather(*coroutine)

        return JsonResponse(response_data)
