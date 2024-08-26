import pytest
from Nonogram.NonogramBoard import NonogramGameplay
from NonogramServer.models import NonogramBoard
from src.utils import GameBoardCellState
from src.utils import RealBoardCellState
from src.utils import serialize_gameboard
from src.utils import Config


@pytest.mark.django_db
def test_nonogram_board_mark(
    test_boards,
):
    for test_board in test_boards:
        board_id = test_board["board_id"]
        board = test_board["board"]
        board_str = serialize_gameboard(test_board["board"])
        num_row = test_board["num_row"]
        num_column = test_board["num_column"]
        black_counter = test_board["black_counter"]
        board_data = NonogramBoard(
            board_id=board_id,
            board=board_str,
            num_row=num_row,
            num_column=num_column,
            black_counter=black_counter,
            theme="test data"
        )

        game_board = NonogramGameplay(
            data=board_data,
            db_sync=False
        )

        for x in range(num_row):
            for y in range(num_column):
                expected_result = Config.CELL_APPLIED if black_counter > 0 else Config.BOARD_GAME_OVER
                assert game_board.mark(x, y, GameBoardCellState.MARK_X) == expected_result
                assert game_board.mark(x, y, GameBoardCellState.MARK_QUESTION) == expected_result
                assert game_board.mark(x, y, GameBoardCellState.NOT_SELECTED) == expected_result

                if board[x][y] == RealBoardCellState.BLACK:
                    expected_result = Config.CELL_APPLIED
                elif black_counter > 0:
                    expected_result = Config.CELL_UNCHANGED
                else:
                    expected_result = Config.BOARD_GAME_OVER

                assert game_board.mark(x, y, GameBoardCellState.REVEALED) == expected_result

                if expected_result == Config.CELL_APPLIED:
                    black_counter -= 1
                    expected_result = Config.CELL_UNCHANGED if black_counter > 0 else Config.BOARD_GAME_OVER
                elif expected_result == Config.CELL_UNCHANGED:
                    expected_result = Config.CELL_APPLIED

                assert game_board.mark(x, y, GameBoardCellState.MARK_X) == expected_result
                assert game_board.mark(x, y, GameBoardCellState.MARK_QUESTION) == expected_result
                assert game_board.mark(x, y, GameBoardCellState.NOT_SELECTED) == expected_result
