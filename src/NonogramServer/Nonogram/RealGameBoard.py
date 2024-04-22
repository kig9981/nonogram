from NonogramServer.models import NonogramBoard
import json
from Nonogram.utils import deserialize_gameboard


class RealGameBoard:
    def __init__(
        self,
        board_id: int,
    ):
        self.board_id = board_id
        try:
            board_str = NonogramBoard.objects.get(pk=board_id)
            self.board = deserialize_gameboard(board_str)

        except NonogramBoard.DoesNotExist:
            raise "board_id not exist"
        except ValueError as error:
            raise error
