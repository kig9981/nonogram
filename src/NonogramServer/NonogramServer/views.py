from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from .models import NonogramBoard
from .models import Session
from .models import History
from Nonogram.utils import get_from_db
from Nonogram.utils import deserialize_gameboard
from Nonogram.utils import deserialize_gameplay
from Nonogram.NonogramBoard import NonogramGameplay
import json


def process_board_query(
    query: dict,
) -> HttpResponse:
    board_id = query['board_id']

    board_data = get_from_db(
        model_class=NonogramBoard,
        label=f"board_id {board_id}",
        board_id=board_id,
    )

    response_data = {
        "board": deserialize_gameboard(board_data.board),
        "num_row": board_data.num_row,
        "num_column": board_data.num_column,
    }

    return JsonResponse(response_data)


def process_gameplay_query(
    query: dict,
) -> HttpResponse:
    GAME_NOT_START = 0
    session_id = query['session_id']
    game_turn = query['game_turn']

    session = get_from_db(
        model_class=Session,
        label=f"session_id {session_id}",
        session_id=session_id,
    )

    board_data = NonogramBoard.objects.get(pk=session.board_id)

    if game_turn == GAME_NOT_START:
        response_data = {
            "board": board_data.board,
            "num_row": board_data.num_row,
            "num_column": board_data.num_column,
        }

        return JsonResponse(response_data)

    latest_turn_info = History.objects.get(pk=session.current_game_id)
    latest_turn = latest_turn_info.number_of_turn

    if game_turn < 0 or game_turn > latest_turn:
        return HttpResponseBadRequest(f"invalid game_turn. must be between 0 to {latest_turn}(latest turn)")

    board = None

    if game_turn == latest_turn:
        board = deserialize_gameplay(
            serialized_string=latest_turn_info.board,
            return_int=True,
        )
    else:
        gameplay = NonogramGameplay(session.board_id)

        moves = History.objects.filter(
            session_id=session.session_id,
            gameplay_id=latest_turn_info.gameplay_id,
            current_turn__lte=game_turn,
        )

        for move in moves:
            gameplay.mark(
                x=move.x_coord,
                y=move.y_coord,
                new_state=move.type_of_move,
            )

        board = gameplay.get_int_board()

    response_data = {
        "board": board,
        "num_row": board_data.num_row,
        "num_column": board_data.num_column,
    }

    return JsonResponse(response_data)


# Create your views here.
def get_nonogram_board(request: HttpRequest):
    '''
    노노그램 보드에 대한 정보를 반환하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (int): 유저의 세션 id
        board_id (int): 게임보드의 id, session_id가 0인 경우에 참조한다.
        game_turn (int): 원하는 턴 수. session_id가 0이 아닌 경우 참조한다.

    Returns:
        session_id가 0이 아닌경우, 해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        존재한다면 board_id와 game_turn을 참조해서 게임 진행 상황을 반환.
        board_id가 존재하지 않는다면 404에러(board_id not found)를 반환.
        game_turn이 0인 경우 현재 플레이어의 게임보드를 리턴.
        game_turn이 음수이거나 현재 진행 턴보다 큰 경우 400에러(invalid game_turn)를 반환.
        이외의 경우에는 선택한 턴의 게임 진행 정보를 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        board (list[list]): [요청한 게임보드/게임 진행 정보를 반영한 게임보드]를 2차원 배열로 반환.
                            각 원소의 값은 Nonogram.utils의 GameBoardCellState, RealBoardCellState 참조.
        num_row (int): 게임보드의 행 수
        num_column (int): 게임보드의 열 수
    '''
    if request.method == "GET":
        return HttpResponse("get_nonogram_board(get)")
    else:
        BOARD_ID_QUERY = 0
        query = json.loads(request.body)
        try:
            session_id = query['session_id']
            if session_id == BOARD_ID_QUERY:
                return process_board_query(query)
            else:
                return process_gameplay_query(query)
        except KeyError as error:
            return HttpResponseBadRequest(f"{error} is missing.")
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")


def set_cell_state(request: HttpRequest):
    '''
    진행중인 게임의 특정 cell의 상태를 변화시키는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (int): 유저의 세션 id
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
    '''
    if request.method == "GET":
        return HttpResponse("set_cell_state(get)")
    else:
        return HttpResponse("set_cell_state(post)")


def create_new_session(request: HttpRequest):
    '''
    새로운 세션을 생성하는 메서드.
    Args:
        None
    Returns:
        요청한 사항에 대한 응답을 json형식으로 리턴.
        session_id: 생성에 성공한 경우 해당 session_id, 실패한 경우 0을 반환
    '''
    if request.method == "GET":
        return HttpResponse("create_new_session(get)")
    else:
        return HttpResponse("create_new_session(post)")


def create_new_game(request: HttpRequest):
    '''
    특정 세션에서 새 게임을 시작하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (int): 유저의 세션 id
        force_new_game (bool): 이미 진행중인 게임을 강제로 종료 후 시작할지 여부
    Returns:
        요청한 사항에 대한 응답을 json형식으로 리턴.
        session_id: 생성에 성공한 경우 해당 session_id, 실패한 경우 0을 반환

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        response (int): 적용 여부에 따라 응답 코드를 반환.
                        0=GAME_EXIST
                        1=NEW_GAME_STARTED
    '''
    if request.method == "GET":
        return HttpResponse("create_new_game(get)")
    else:
        return HttpResponse("create_new_game(post)")
