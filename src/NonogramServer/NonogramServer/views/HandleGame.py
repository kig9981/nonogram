import json
from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from ..models import NonogramBoard
from ..models import Session
from Nonogram.NonogramBoard import NonogramGameplay
from utils import async_get_from_db
from utils import is_uuid4
from utils import deserialize_gameboard


class HandleGame(AsyncAPIView):
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
        session_id: str,
    ) -> HttpResponse:
        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"session_id '{session_id}' is not valid id.")
        
        try:
            session_data = await async_get_from_db(
                model_class=Session,
                label=f"session_id '{session_id}'",
                select_related=['current_game', 'board_data'],
                session_id=session_id,
            )
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")
        
        board_data = session_data.board_data
        
        if board_data is None:
            return HttpResponseNotFound("board data not found.")
        
        response_data = {
            "board": deserialize_gameboard(board_data.board),
            "num_row": board_data.num_row,
            "num_column": board_data.num_column,
        }

        return JsonResponse(response_data)

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
        GAME_EXIST = 0
        NEW_GAME_STARTED = 1
        query = json.loads(request.body)
        if 'board_id' not in query:
            return HttpResponseBadRequest("board_id is missing.")

        board_id = query['board_id']

        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"session_id '{session_id}' is not valid id.")
        if board_id != RANDOM_BOARD and (not isinstance(board_id, str) or not is_uuid4(board_id)):
            return HttpResponseBadRequest(f"board_id '{board_id}' is not valid id.")

        try:
            session_data = await async_get_from_db(
                model_class=Session,
                label=f"session_id '{session_id}'",
                select_related=['current_game', 'board_data'],
                session_id=session_id,
            )
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")

        if session_data.board_data is not None:
            if not force_new_game:
                response_data = {
                    "response": GAME_EXIST,
                    "board_id": session_data.board_data.board_id,
                }
                return JsonResponse(response_data)

            session = NonogramGameplay(session_data)
            await session.async_reset()

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

        session = NonogramGameplay(
            data=board_data,
            session_id=session_id,
            delayed_save=True
        )

        await session.asave()

        response_data = {
            "response": NEW_GAME_STARTED,
            "board_id": board_id,
        }

        return JsonResponse(response_data)
