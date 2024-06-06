from django.apps import AppConfig
from django.db.models.signals import post_migrate
from utils import serialize_gameboard
from utils import RealBoardCellState
import uuid

default_board = [
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1],
    [0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1],
    [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0],
    [1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1],
    [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1],
    [0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0],
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1],
    [0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0]
]

default_board2 = [
    [1, 0, 1, 0, 0, 1, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 1, 1, 1],
    [1, 1, 0, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1, 0, 0, 1],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 0, 1, 1, 1, 0, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 1, 0, 1, 1, 0, 0],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1]
]


def add_default_data(sender, **kwargs):
    from .models import NonogramBoard
    if not NonogramBoard.objects.exists():
        NonogramBoard.objects.create(
            board_id=str(uuid.uuid4()),
            board=serialize_gameboard(default_board),
            num_row=len(default_board),
            num_column=len(default_board[0]),
            black_counter=sum(
                sum(1 for item in row if item == RealBoardCellState.BLACK)
                for row in default_board
            ),
            theme="default",
        )

        NonogramBoard.objects.create(
            board_id=str(uuid.uuid4()),
            board=serialize_gameboard(default_board2),
            num_row=len(default_board2),
            num_column=len(default_board2[0]),
            black_counter=sum(
                sum(1 for item in row if item == RealBoardCellState.BLACK)
                for row in default_board2
            ),
            theme="default",
        )




class NonogramserverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'NonogramServer'

    def ready(self):
        post_migrate.connect(add_default_data, sender=self)
