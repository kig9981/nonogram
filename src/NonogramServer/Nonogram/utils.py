from enum import IntEnum
import json
from typing import List
from typing import Union


class RealBoardCellStatus(IntEnum):
    UNKNOWN = -1
    WHITE = 0
    BLACK = 1


class GameBoardCellStatus(IntEnum):
    NOT_SELECTED = 0
    REVEALED = 1
    MARK_X = 2
    MARK_QUESTION = 3


def validate_gameboard(
    board: List[List[Union[int, RealBoardCellStatus]]]
) -> None:
    if not board or not isinstance(board, list):
        raise ValueError("Invalid gameboard(Invalid type).")

    row_length = len(board[0])

    for row in board:
        if len(row) != row_length:
            raise ValueError("Invalid gameboard(Row length error).")

        for item in row:
            if not isinstance(item, int) or not isinstance(item, RealBoardCellStatus):
                raise ValueError("Invalid gameboard(Invalid item type)")
            if isinstance(item, int) and not (-1 <= item <= 1):
                raise ValueError("Invalid gameboard(Invalid range(-1 ~ 1))")


def deserialize_gameboard(
    serialized_string: str
) -> List[List[RealBoardCellStatus]]:
    board = json.loads(serialized_string)
    try:
        validate_gameboard(board)
    except ValueError as error:
        raise ValueError("Failed to deserialize : " + str(error))

    board = [
        [RealBoardCellStatus(item) for item in row]
        for row in board
    ]

    return board


def serialize_gameboard(
    board: List[List[RealBoardCellStatus]]
) -> str:
    try:
        validate_gameboard(board)
    except ValueError as error:
        raise ValueError("Failed to serialize : " + str(error))

    board = [
        [int(item) for item in row]
        for row in board
    ]

    serialize_string = json.dumps(board)

    return serialize_string
