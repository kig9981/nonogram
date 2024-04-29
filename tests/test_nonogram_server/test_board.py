import pytest
from Nonogram.NonogramBoard import NonogramGameplay
from Nonogram.utils import deserialize_gameboard
from Nonogram.utils import GameBoardCellState
from Nonogram.utils import RealBoardCellState


@pytest.mark.django_db
def test_nonogram_board_mark(test_boards):
    for test_board in test_boards:
        board_id = test_board["board_id"]
        board = deserialize_gameboard(test_board["board"])
        num_row = test_board["num_row"]
        num_column = test_board["num_column"]

        game_board = NonogramGameplay(board_id)

        for x in range(num_row):
            for y in range(num_column):
                assert game_board.mark(x, y, GameBoardCellState.MARK_X)
                assert game_board.mark(x, y, GameBoardCellState.MARK_QUESTION)
                assert game_board.mark(x, y, GameBoardCellState.NOT_SELECTED)

                result = game_board.mark(x, y, GameBoardCellState.REVEALED)

                assert (board[x][y] == RealBoardCellState.BLACK) == result

                if board[x][y] == RealBoardCellState.WHITE:
                    assert not result
                    assert game_board.mark(x, y, GameBoardCellState.MARK_X)
                    assert game_board.mark(x, y, GameBoardCellState.MARK_QUESTION)
                    assert game_board.mark(x, y, GameBoardCellState.NOT_SELECTED)
                else:
                    assert result
                    assert not game_board.mark(x, y, GameBoardCellState.MARK_X)
                    assert not game_board.mark(x, y, GameBoardCellState.MARK_QUESTION)
                    assert not game_board.mark(x, y, GameBoardCellState.NOT_SELECTED)