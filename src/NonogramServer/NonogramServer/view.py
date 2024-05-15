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
