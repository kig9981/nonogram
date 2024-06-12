import json
import uuid
import io
import base64
from drfasyncview import AsyncAPIView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from ..models import NonogramBoard
from utils import RealBoardCellState
from utils import is_base64
from PIL import Image


class AddNonogramBoard(AsyncAPIView):
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
    async def post(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
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
        if not is_base64(base64_board_data):
            return HttpResponseBadRequest("invalid base64 string")
        try:
            board_image_data = base64.b64decode(base64_board_data)
            board_image = Image.open(io.BytesIO(board_image_data))
            board_image.verify()

            board_image = Image.open(io.BytesIO(board_image_data))
            board_image.load()
        except Exception:
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

        await nonogram_board.asave()

        response_data = {
            "board_id": board_id,
        }

        return JsonResponse(response_data)
