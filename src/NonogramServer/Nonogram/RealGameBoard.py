from NonogramServer.models import NonogramBoard
from Nonogram.utils import deserialize_gameboard
from Nonogram.utils import RealBoardCellState
from django.core.exceptions import ObjectDoesNotExist
from typing import List
from typing import Union
from typing import Optional


class RealGameBoard:
    def __init__(
        self,
        board_id: int,
        board: Optional[List[List[Union[RealBoardCellState, int]]]] = None,
    ):
        self.board_id = board_id
        if board is None:
            try:
                board_data = NonogramBoard.objects.get(pk=board_id)
                self.board = deserialize_gameboard(board_data.board)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist("board_id not exist")
            except ValueError as error:
                raise error
        else:
            self.board = board

        self.num_row = len(self.board)
        self.num_column = len(self.board[0])
