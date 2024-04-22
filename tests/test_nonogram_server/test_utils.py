from src.NonogramServer.Nonogram.utils import validate_gameboard
from src.NonogramServer.Nonogram.utils import deserialize_gameboard
from src.NonogramServer.Nonogram.utils import serialize_gameboard


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
    pass


def test_serialize_gameboard():
    pass
