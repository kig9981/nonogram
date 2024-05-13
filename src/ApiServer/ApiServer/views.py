import json
from django.shortcuts import render
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
import environ


env = environ.Env()
environ.Env.read_env()
NONOGRAM_SERVER_PROTOCOL = env("NONOGRAM_SERVER_PROTOCOL")
NONOGRAM_SERVER_HOST = env("NONOGRAM_SERVER_HOST")
NONOGRAM_SERVER_PORT = env("NONOGRAM_SERVER_PORT")
NONOGRAM_SERVER_URL = f"{NONOGRAM_SERVER_PROTOCOL}://{NONOGRAM_SERVER_HOST}:{NONOGRAM_SERVER_PORT}"


# Create your views here.
async def get_nonogram_board(request: HttpRequest):
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
    if request.method == "GET":
        return HttpResponse("get_nonogram_board(get)")
    else:
        GAMEBOARD_QUERY = 0

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


async def get_nonogram_play(request: HttpRequest):
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
    if request.method == "GET":
        return HttpResponse("get_nonogram_play(get)")
    else:
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
                "board": response["board"],
                "latest_turn": response["latest_turn"],
            }
            return JsonResponse(response_data)

        elif status_code == HTTPStatus.NOT_FOUND:
            return HttpResponseNotFound(response["response"])
        else:
            return HttpResponseServerError("unknown error")


async def synchronize(request: HttpRequest):
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
    if request.method == "GET":
        return HttpResponse("synchronize(get)")
    else:
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


async def make_move(request: HttpRequest):
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
    if request.method == "GET":
        return HttpResponse("make_move(get)")
    else:
        if request.content_type != "application/json":
            return HttpResponseBadRequest("Must be Application/json request.")

        query = json.loads(request.body)

        if "session_id" not in query:
            return HttpResponseBadRequest("session_id is missing.")
        if "x" not in query:
            return HttpResponseBadRequest("x is missing.")
        if "y" not in query:
            return HttpResponseBadRequest("y is missing.")
        if "state" not in query:
            return HttpResponseBadRequest("state is missing.")

        session_id = query["session_id"]
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


async def create_new_session(request: HttpRequest):
    '''
    새 세션을 생성하는 메서드.
    Args:

    Returns:
        만들어진 session id를 반환

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        session_id (str): session_id를 uuid형식으로 반환.
    '''
    if request.method == "GET":
        return HttpResponse("create_new_session(get)")
    else:
        # TODO: 비정상적인 쿼리에 대한 거부(같은 ip에 대해서 쿨타임 설정)
        url = f"{NONOGRAM_SERVER_URL}/create_new_session"
        response = await send_request(
            url=url,
            request={},
        )
        status_code = response["status_code"]

        if status_code == HTTPStatus.OK:
            response_data = {
                "session_id": response["session_id"],
            }
            return JsonResponse(response_data)
        else:
            return HttpResponseServerError("unknown error")


async def create_new_game(request: HttpRequest):
    '''
    세션에서 새 게임을 시작하는 메서드.
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        session_id (str): 유저의 세션 id
    Returns:
        해당 session_id가 존재하지 않는다면 404에러(session_id not found)를 반환.
        존재한다면 board_id와 게임 보드 정보를 반환.

        성공적일 경우 요청한 사항에 대한 응답을 json형식으로 리턴.
        board_id (str): 새로 시작한 board_id정보를 uuid형식으로 반환.
        board (list[list]): 게임보드를 2차원 배열로 반환.
                            각 원소의 값은 Nonogram.utils의 GameBoardCellState, RealBoardCellState 참조.
        num_row (int): 게임보드의 행 수
        num_column (int): 게임보드의 열 수
    '''
    if request.method == "GET":
        return HttpResponse("create_new_game(get)")
    else:
        return HttpResponse("create_new_game(post)")
