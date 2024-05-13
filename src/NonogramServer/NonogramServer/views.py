from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from .models import NonogramBoard
from .models import Session
from .models import History
from utils import GameBoardCellState
from utils import RealBoardCellState
from utils import async_get_from_db
from utils import serialize_gameboard
from utils import deserialize_gameboard
from utils import deserialize_gameplay
from Nonogram.NonogramBoard import NonogramGameplay
from Nonogram.RealGameBoard import RealGameBoard
from PIL import Image
from PIL import UnidentifiedImageError
import json
import uuid
import asyncio
import io
import base64
import re


async def process_board_query(
    query: dict,
) -> HttpResponse:
    board_id = query['board_id']

    board_data = await async_get_from_db(
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


async def process_gameplay_query(
    query: dict,
) -> HttpResponse:
    GAME_NOT_START = 0
    LATEST_TURN = -1
    session_id = query['session_id']
    game_turn = query['game_turn']

    session = await async_get_from_db(
        model_class=Session,
        label=f"session_id {session_id}",
        select_related=['board_data', 'current_game'],
        session_id=session_id,
    )

    board_data = session.board_data

    if game_turn == GAME_NOT_START:
        if board_data is None:
            return HttpResponseNotFound("board not found.")
        response_data = {
            "board_id": str(board_data.board_id),
            "board": board_data.board,
            "num_row": board_data.num_row,
            "num_column": board_data.num_column,
        }

        return JsonResponse(response_data)

    latest_turn_info = session.current_game
    latest_turn = 0 if latest_turn_info is None else latest_turn_info.current_turn

    if not isinstance(game_turn, int) or not (-1 <= game_turn <= latest_turn):
        return HttpResponseBadRequest(f"invalid game_turn. must be between 0 to {latest_turn}(latest turn)")

    if game_turn == latest_turn or game_turn == LATEST_TURN:
        if board_data is None:
            return HttpResponseNotFound("board not found.")
        board = deserialize_gameplay(
            serialized_string=session.board,
            return_int=True,
        )
    else:
        board_id = session.board_data.board_id
        board = deserialize_gameboard(session.board_data.board)
        real_board = RealGameBoard(
            board_id=board_id,
            board=board,
        )

        gameplay = NonogramGameplay(
            board_id=board_id,
            board=real_board,
        )

        async for move in History.objects.filter(
            current_session=session,
            gameplay_id=latest_turn_info.gameplay_id,
            current_turn__lte=game_turn,
        ).order_by("current_turn"):
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
        "latest_turn": latest_turn,
    }

    return JsonResponse(response_data)


# Create your views here.
async def get_nonogram_board(request: HttpRequest):
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
    if request.method == "GET":
        return HttpResponse("get_nonogram_board(get)")
    else:
        BOARD_ID_QUERY = 0
        query = json.loads(request.body)
        try:
            session_id = query['session_id']
            if session_id == BOARD_ID_QUERY:
                return await process_board_query(query)
            else:
                return await process_gameplay_query(query)
        except KeyError as error:
            return HttpResponseBadRequest(f"{error} is missing.")
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")
        except ValidationError as error:
            return HttpResponseBadRequest(f"'{error.message}' is not valid id.")


async def set_cell_state(request: HttpRequest):
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
                        0(or False)=UNCHANGED
                        1(or True)=APPLIED
    '''
    if request.method == "GET":
        return HttpResponse("set_cell_state(get)")
    else:
        query = json.loads(request.body)
        try:
            session_id = query['session_id']
            x = query['x_coord']
            y = query['y_coord']
            new_state = query['new_state']
            session = await async_get_from_db(
                model_class=Session,
                label=f"session_id {session_id}",
                select_related=['current_game', 'board_data'],
                session_id=session_id,
            )

            if session.board_data is None:
                return HttpResponseNotFound("gameplay not found.")

            board_data = session.board_data
            num_row = board_data.num_row
            num_column = board_data.num_column
            if not isinstance(x, int) or not isinstance(y, int) or not (0 <= x < num_row) or not (0 <= y < num_column):
                return HttpResponseBadRequest("Invalid coordinate.")
            if not isinstance(new_state, int) or not (0 <= new_state <= 3):
                return HttpResponseBadRequest("Invalid state. Either 0(NOT_SELECTED), 1(REVEALED), 2(MARK_X), or 3(MARK_QUESTION).")
            changed = await session.async_mark(x, y, new_state)
            response_data = {"response": changed}
            return JsonResponse(response_data)
        except KeyError as error:
            return HttpResponseBadRequest(f"{error} is missing.")
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")
        except ValidationError as error:
            return HttpResponseBadRequest(f"'{error.message}' is not valid id.")


async def create_new_session(request: HttpRequest):
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
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id)
        await session.asave()
        response_data = {"session_id": session_id}
        return JsonResponse(response_data)


async def create_new_game(request: HttpRequest):
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
    if request.method == "GET":
        return HttpResponse("create_new_game(get)")
    else:
        RANDOM_BOARD = 0
        GAME_EXIST = 0
        NEW_GAME_STARTED = 1
        query = json.loads(request.body)
        try:
            session_id = query['session_id']
            board_id = query['board_id']
            force_new_game = query['force_new_game']

            if not isinstance(session_id, str) or (not isinstance(board_id, str) and board_id != RANDOM_BOARD) or not isinstance(force_new_game, bool):
                return HttpResponseBadRequest("invalid type.")

            session = await async_get_from_db(
                model_class=Session,
                label=f"session_id {session_id}",
                select_related=['current_game', 'board_data'],
                session_id=session_id,
            )

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
                board_data = await async_get_from_db(
                    model_class=NonogramBoard,
                    label=f"board_id {board_id}",
                    board_id=board_id,
                )

            session.board_data = board_data
            session.board = serialize_gameboard(
                [
                    [GameBoardCellState.NOT_SELECTED for _ in range(board_data.num_column)]
                    for _ in range(board_data.num_row)
                ]
            )
            session.current_game = None

            coroutine.append(asyncio.create_task(session.asave()))

            response_data = {
                "response": NEW_GAME_STARTED,
                "board_id": board_id,
            }

            await asyncio.gather(*coroutine)

            return JsonResponse(response_data)

        except KeyError as error:
            return HttpResponseBadRequest(f"{error} is missing.")
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")
        except ValidationError as error:
            return HttpResponseBadRequest(f"'{error.message}' is not valid id.")


async def add_nonogram_board(request: HttpRequest):
    '''
    새 노노그램 보드를 db에 추가하는 메서드
    Args:
        Application/json으로 요청을 받는 것을 전제로 한다.
        board (str): 이미지의 base64 데이터
        num_row (int) : 추가하려는 노노그램 게임의 행의 수
        num_column (int) : 추가하려는 노노그램 게임의 열의 수
        theme (str, optional): 이미지의 테마.
    Returns:
        요청한 사항에 대한 응답을 json형식으로 리턴.
        만약 valid한 base64문자열이 아니면 400에러(invalid base64 string) 리턴.
        base64로 디코딩한 것이 PIL 이미지가 아니면 400에러(invalid image format) 리턴
        board_id (str): 생성한 board_id의 uuid를 리턴, 실패시 빈 문자열을 리턴.
    '''
    if request.method == "GET":
        return HttpResponse("add_nonogram_board(get)")
    else:
        BLACK_THRESHOLD = 127
        query = json.loads(request.body)
        try:
            base64_board_data = query['board']
            num_row = query['num_row']
            num_column = query['num_column']
            theme = query['theme'] if 'theme' in query else ''
            if not isinstance(base64_board_data, str) or not isinstance(num_row, int) or not isinstance(num_column, int) or not isinstance(theme, str):
                return HttpResponseBadRequest("invalid type.")
            if not re.fullmatch('[A-Za-z0-9+/]*={0,2}', base64_board_data):
                return HttpResponseBadRequest("invalid base64 string")
            board_image_data = base64.b64decode(base64_board_data)
            board_image = Image.open(io.BytesIO(board_image_data))

            board_image.load()
            board_image.verify()

            board_id = str(uuid.uuid4())

            bw_board_image = board_image.convert('1')
            resized_board_image = bw_board_image.resize((num_row, num_column))
            pixels = resized_board_image.load()

            board = [
                [int(RealBoardCellState.BLACK) if pixels[x, y] <= BLACK_THRESHOLD else int(RealBoardCellState.WHITE) for y in range(num_column)]
                for x in range(num_row)
            ]

            black_counter = sum(
                sum(1 for item in row if item == RealBoardCellState.BLACK)
                for row in board
            )

            nonogram_board = NonogramBoard(
                board_id=board_id,
                board=board,
                num_row=num_row,
                num_column=num_column,
                theme=theme,
                black_counter=black_counter,
            )

            # TODO: 비동기 task queue를 사용해서 업데이트하는 로직으로 변경
            await nonogram_board.asave()

            response_data = {
                "board_id": board_id,
            }

            return JsonResponse(response_data)

        except KeyError as error:
            return HttpResponseBadRequest(f"{error} is missing.")
        except (ValueError, UnidentifiedImageError):
            return HttpResponseBadRequest("invalid image data.")
