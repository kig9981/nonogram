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
from utils import GameBoardCellState
from utils import RealBoardCellState
from utils import async_get_from_db
from utils import serialize_gameboard
from utils import deserialize_gameboard
from utils import deserialize_gameplay
from utils import is_uuid4
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
                        0=UNCHANGED
                        1=APPLIED
                        2=GAME_OVER
    '''
    if request.method == "GET":
        return HttpResponse("set_cell_state(get)")
    else:
        GAME_OVER = 2
        if request.content_type != "application/json":
            return HttpResponseBadRequest("Must be Application/json request.")
        query = json.loads(request.body)
        if 'session_id' not in query:
            return HttpResponseBadRequest("session_id is missing.")
        if 'x_coord' not in query:
            return HttpResponseBadRequest("x_coord is missing.")
        if 'y_coord' not in query:
            return HttpResponseBadRequest("y_coord is missing.")
        if 'new_state' not in query:
            return HttpResponseBadRequest("new_state is missing.")
        session_id = query['session_id']
        x = query['x_coord']
        y = query['y_coord']
        new_state = query['new_state']
        if not isinstance(session_id, str) or not is_uuid4(session_id):
            return HttpResponseBadRequest(f"session_id '{session_id}' is not valid id.")
        try:
            session = await async_get_from_db(
                model_class=Session,
                label=f"session_id '{session_id}'",
                select_related=['current_game', 'board_data'],
                session_id=session_id,
            )
        except ObjectDoesNotExist as error:
            return HttpResponseNotFound(f"{error} not found.")

        if session.board_data is None:
            return HttpResponseNotFound("gameplay not found.")

        board_data = session.board_data
        num_row = board_data.num_row
        num_column = board_data.num_column
        if not isinstance(x, int) or not isinstance(y, int) or not (0 <= x < num_row) or not (0 <= y < num_column):
            return HttpResponseBadRequest("Invalid coordinate.")
        if not isinstance(new_state, int) or not (0 <= new_state <= 3):
            return HttpResponseBadRequest("Invalid state. Either 0(NOT_SELECTED), 1(REVEALED), 2(MARK_X), or 3(MARK_QUESTION).")
        if session.unrevealed_counter > 0:
            changed = 1 if await session.async_mark(x, y, new_state) else 0
        else:
            changed = GAME_OVER
        response_data = {"response": changed}
        return JsonResponse(response_data)


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
        if request.content_type != "application/json":
            return HttpResponseBadRequest("Must be Application/json request.")
        query = json.loads(request.body)
        if 'board' not in query:
            return HttpResponseBadRequest("board is missing.")
        if 'num_row' not in query:
            return HttpResponseBadRequest("num_row is missing.")
        if 'num_column' not in query:
            return HttpResponseBadRequest("num_column is missing.")
        base64_board_data = query['board']
        num_row = query['num_row']
        num_column = query['num_column']
        theme = query['theme'] if 'theme' in query else ''
        if not isinstance(base64_board_data, str) or not isinstance(num_row, int) or not isinstance(num_column, int) or not isinstance(theme, str):
            return HttpResponseBadRequest("invalid type.")
        if not re.fullmatch('[A-Za-z0-9+/]*={0,2}', base64_board_data):
            return HttpResponseBadRequest("invalid base64 string")
        try:
            board_image_data = base64.b64decode(base64_board_data)
            board_image = Image.open(io.BytesIO(board_image_data))

            board_image.load()
            board_image.verify()
        except (ValueError, UnidentifiedImageError):
            return HttpResponseBadRequest("invalid image data.")

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
