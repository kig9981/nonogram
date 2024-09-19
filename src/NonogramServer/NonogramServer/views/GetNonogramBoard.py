from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from ..models import NonogramBoard
from utils import async_get_from_db
from utils import deserialize_gameboard
from utils import is_uuid4
from utils import LogSystem
from .configure import LOG_PATH


class GetNonogramBoard(AsyncAPIView):
    '''
    노노그램 보드에 대한 정보를 반환하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id
        board_id (str): 게임보드의 id, session_id가 0인 경우에 참조한다.
        game_turn (int): 원하는 턴 수. session_id가 0이 아닌 경우 참조한다.

    Returns:
        session_id가 0이 아닌경우, 해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        존재한다면 board_id와 game_turn을 참조해서 게임 진행 상황을 반환.
        board_id가 존재하지 않는다면 404에러(board_id not found)를 반환.
        game_turn이 0인 경우 현재 플레이어의 게임보드를 리턴. 만약 진행중인 게임이 없다면 404에러(board not found)를 반환
        game_turn이 -1보다 작거나 현재 진행 턴보다 큰 경우 400에러(invalid game_turn)를 반환.
        -1은 가장 최근 턴을 반환
        이외의 경우에는 선택한 턴의 게임 진행 정보를 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        board_id (str): game_turn이 0인 경우에 해당 보드의 id를 반환.
        board (list[list]): [요청한 게임보드/게임 진행 정보를 반영한 게임보드]를 2차원 배열로 반환.
                            각 원소의 값은 Nonogram.utils의 GameBoardCellState, RealBoardCellState 참조.
        num_row (int): 게임보드의 행 수
        num_column (int): 게임보드의 열 수
        latest_turn (int): 게임 진행 정보를 반환할 경우만 가장 최근 턴 수를 반환.
    '''
    logger = LogSystem(
        module_name=__name__,
        log_path=LOG_PATH,
    )

    @logger.log
    async def get(
        self,
        request: HttpRequest,
        board_id: str,
    ) -> HttpResponse:
        if not isinstance(board_id, str) or not is_uuid4(board_id):
            return HttpResponseBadRequest(f"board_id '{board_id}' is not valid id.")
        
        cached_board_data = await cache.aget(f"BD|{board_id}")

        if cached_board_data:
            response_data = {
                "board": deserialize_gameboard(cached_board_data),
                "num_row": len(cached_board_data),
                "num_column": len(cached_board_data[0]),
            }

            return JsonResponse(response_data)

        try:
            board_data = await async_get_from_db(
                model_class=NonogramBoard,
                label=f"board_id '{board_id}'",
                board_id=board_id,
            )
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")
        
        await cache.aset(f"BD|{board_id}", board_data.board, 180)

        response_data = {
            "board": deserialize_gameboard(board_data.board),
            "num_row": board_data.num_row,
            "num_column": board_data.num_column,
        }

        return JsonResponse(response_data)
