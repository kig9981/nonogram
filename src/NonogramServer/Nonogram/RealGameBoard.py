from NonogramServer.models import NonogramBoard
from Nonogram.utils import deserialize_gameboard
from django.core.exceptions import ObjectDoesNotExist


class RealGameBoard:
    def __init__(
        self,
        board_id: int,
    ):
        self.board_id = board_id
        try:
            board_data = NonogramBoard.objects.get(pk=board_id)
            self.board = deserialize_gameboard(board_data.board)

        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("board_id not exist")
        except ValueError as error:
            raise error

        self.num_row = len(self.board)
        self.num_column = len(self.board[0])
