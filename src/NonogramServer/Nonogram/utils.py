from enum import IntEnum
import json
from typing import List
from typing import Union
from django.db.models import Model
from django.core.exceptions import ObjectDoesNotExist


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
) -> bool:
    if not board or not isinstance(board, list):
        raise ValueError("Invalid gameboard(Invalid type).")

    valid_gameboard = True

    row_length = len(board[0])

    for row in board:
        if len(row) != row_length:
            raise ValueError("Invalid gameboard(Row length error).")

        for item in row:
            if not isinstance(item, int) and not isinstance(item, RealBoardCellStatus):
                raise ValueError("Invalid gameboard(Invalid item type).")
            if isinstance(item, int) and not (-1 <= item <= 1):
                raise ValueError("Invalid gameboard(Invalid range(-1 ~ 1)).")
            if int(item) == -1:
                valid_gameboard = False

    return valid_gameboard


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


def get_from_db(
    model_class: Model,
    label: str,
    **kwargs,
):
    try:
        query = model_class.objects.get(**kwargs)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(label)
    return query


def validate_gameplay(
    board: List[List[Union[int, GameBoardCellStatus]]]
) -> None:
    if not board or not isinstance(board, list):
        raise ValueError("Invalid gameplay(Invalid type).")

    row_length = len(board[0])

    for row in board:
        if len(row) != row_length:
            raise ValueError("Invalid gameplay(Row length error).")

        for item in row:
            if not isinstance(item, int) and not isinstance(item, GameBoardCellStatus):
                raise ValueError("Invalid gameplay(Invalid item type).")
            if isinstance(item, int) and not (0 <= item <= 3):
                raise ValueError("Invalid gameplay(Invalid range(0 ~ 3)).")


def deserialize_gameplay(
    serialized_string: str
) -> List[List[GameBoardCellStatus]]:
    board = json.loads(serialized_string)
    try:
        validate_gameplay(board)
    except ValueError as error:
        raise ValueError("Failed to deserialize : " + str(error))

    board = [
        [GameBoardCellStatus(item) for item in row]
        for row in board
    ]

    return board


def serialize_gameplay(
    board: List[List[GameBoardCellStatus]]
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
