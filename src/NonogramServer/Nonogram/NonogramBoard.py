from RealGameBoard import RealGameBoard
from utils import GameBoardCellState
from utils import RealBoardCellState


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
    ) -> bool:
        if not (0 <= x < self.num_row) or not (0 <= y < self.num_column):
            raise ValueError("incorrect coordinate")
        current_cell_state = self.playboard[x][y]
        current_cell = self.board.board[x][y]
        if current_cell_state == GameBoardCellState.REVEALED:
            return False
        if new_state == GameBoardCellState.REVEALED:
            if current_cell == RealBoardCellState.BLACK:
                self.playboard[x][y] = new_state
                return True
            return False
        self.playboard[x][y] = new_state
        return current_cell_state != new_state

