from src.NonogramServer.Nonogram.utils import validate_gameboard
from src.NonogramServer.Nonogram.utils import deserialize_gameboard
from src.NonogramServer.Nonogram.utils import serialize_gameboard
from src.NonogramServer.Nonogram.utils import RealBoardCellStatus


def test_validate_gameboard():
    board = [
        [1, 1],
        [1, 1],
    ]

    try:
        result = validate_gameboard(board)
        assert result
    except ValueError as error:
        assert "valid gameboard: should not make exception(" + str(error) + ")" and 0

    board = [
        [1, -1],
        [0, 1],
    ]

    try:
        result = validate_gameboard(board)
        assert not result
    except ValueError:
        assert "valid gameboard: should not make exception" and 0

    board = [
        [1, -1],
        [0, 1, 1],
    ]

    try:
        result = validate_gameboard(board)
        assert "invalid gameboard: should make exception" and 0
    except ValueError as error:
        assert "Invalid gameboard(Row length error)." == str(error)

    board = 14

    try:
        result = validate_gameboard(board)
        assert "invalid gameboard: should make exception" and 0
    except ValueError as error:
        assert "Invalid gameboard(Invalid type)." == str(error)

    board = [
        ["1", "1"],
        ["1", "1"],
    ]

    try:
        result = validate_gameboard(board)
        assert "invalid gameboard: should make exception" and 0
    except ValueError as error:
        assert "Invalid gameboard(Invalid item type)." == str(error)

    board = [
        [1, -1],
        [0, 2],
    ]

    try:
        result = validate_gameboard(board)
        assert "invalid gameboard: should make exception" and 0
    except ValueError as error:
        assert "Invalid gameboard(Invalid range(-1 ~ 1))." == str(error)


def test_deserialize_gameboard():
    board = [
        [1, 1],
        [1, 1],
    ]

    board_str = "[[1, 1], [1, 1]]"

    assert deserialize_gameboard(board_str) == board


def test_serialize_gameboard():
    board = [
        [RealBoardCellStatus.BLACK, RealBoardCellStatus.BLACK],
        [RealBoardCellStatus.BLACK, RealBoardCellStatus.BLACK],
    ]

    board_str = "[[1, 1], [1, 1]]"

    assert serialize_gameboard(board) == board_str
