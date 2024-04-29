from RealGameBoard import RealGameBoard
from utils import GameBoardCellState


class NonogramBoard:
    def __init__(
        self,
        board_id: int,
    ):
        self.board_size = None
        self.board_id = board_id
        self.board = RealGameBoard(board_id)
        self.num_row = self.board.num_row
        self.num_column = self.board.num_column
        self.playboard = [
            [GameBoardCellState.NOT_SELECTED for _ in range(self.num_column)]
            for _ in range(self.num_row)
        ]

    def mark(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,      
    ):
