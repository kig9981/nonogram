import os
import json
from src.utils import validate_gameboard
from src.utils import deserialize_gameboard
from src.utils import serialize_gameboard
from src.utils import validate_gameplay
from src.utils import deserialize_gameplay
from src.utils import serialize_gameplay
from src.utils import RealBoardCellState
from src.utils import GameBoardCellState


def test_validate_gameboard():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_validate_gameboard_path = os.path.join(test_data_path, 'test_validate_gameboard.json')
    with open(test_validate_gameboard_path, 'r') as f:
        test_boards = json.load(f)

    for test_board in test_boards:
        board = test_board["board"]
        valid = test_board["valid"]
        try:
            result = validate_gameboard(board)
            if valid:
                if result != test_board["result"]:
                    assert f"test case <{board}> failed\n error message: should be [{test_board['result']}]" and False
            else:
                assert f"test case <{board}> failed\n error message: invalid gameboard: should make exception" and False
        except ValueError as error:
            if valid:
                assert f"test case <{board}> failed\n error message: valid gameboard: should not make exception" and False
            elif str(error) != test_board["exception_message"]:
                assert f"test case <{board}> failed\n error message: incorrect exception: should be [{test_board['exception_message']}] but [{error}]" and False


def test_deserialize_gameboard():
    board = [
        [1, 1],
        [1, 1],
    ]

    board_str = "[[1, 1], [1, 1]]"

    assert deserialize_gameboard(board_str) == board


def test_serialize_gameboard():
    board = [
        [RealBoardCellState.BLACK, RealBoardCellState.BLACK],
        [RealBoardCellState.BLACK, RealBoardCellState.BLACK],
    ]

    board_str = "[[1, 1], [1, 1]]"

    assert serialize_gameboard(board) == board_str


def test_validate_gameplay():
    cwd = os.path.dirname(__file__)
    test_data_path = os.path.join(cwd, 'test_data')
    test_validate_gameplay_path = os.path.join(test_data_path, 'test_validate_gameplay.json')
    with open(test_validate_gameplay_path, 'r') as f:
        test_boards = json.load(f)

    for test_board in test_boards:
        board = test_board["board"]
        valid = test_board["valid"]
        try:
            validate_gameplay(board)
            if not valid:
                assert f"test case <{board}> failed\n error message: invalid gameplay: should make exception" and False
        except ValueError as error:
            if valid:
                assert f"test case <{board}> failed\n error message: valid gameplay: should not make exception" and False
            elif str(error) != test_board["exception_message"]:
                assert f"test case <{board}> failed\n error message: incorrect exception: should be [{test_board['exception_message']}] but [{error}]" and False


def test_deserialize_gameplay():
    board = [
        [1, 1],
        [1, 1],
    ]

    board_str = "[[1, 1], [1, 1]]"

    assert deserialize_gameplay(board_str) == board


def test_serialize_gameplay():
    board = [
        [GameBoardCellState.REVEALED, GameBoardCellState.REVEALED],
        [GameBoardCellState.REVEALED, GameBoardCellState.REVEALED],
    ]

    board_str = "[[1, 1], [1, 1]]"

    assert serialize_gameplay(board) == board_str
