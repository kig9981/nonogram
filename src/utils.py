from enum import IntEnum
import json
import uuid
import time
import base64
import inspect
import hashlib
import aiohttp
import asyncio
import logging
from http import HTTPStatus
from pathlib import Path
from typing import Any
from typing import List
from typing import Dict
from typing import Union
from typing import Optional
from typing import Callable
from typing import TypeVar
from django.db.models import Model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError


class RealBoardCellState(IntEnum):
    UNKNOWN = -1
    WHITE = 0
    BLACK = 1


class GameBoardCellState(IntEnum):
    NOT_SELECTED = 0
    REVEALED = 1
    MARK_X = 2
    MARK_QUESTION = 3
    MARK_WRONG = 4


def validate_gameboard(
    board: List[List[Union[int, RealBoardCellState]]]
) -> bool:
    if not board or not isinstance(board, list):
        raise ValueError("Invalid gameboard(Invalid type).")

    valid_gameboard = True

    row_length = len(board[0])

    for row in board:
        if len(row) != row_length:
            raise ValueError("Invalid gameboard(Row length error).")

        for item in row:
            if not isinstance(item, int) and not isinstance(item, RealBoardCellState):
                raise ValueError("Invalid gameboard(Invalid item type).")
            if isinstance(item, int) and not (-1 <= item <= 1):
                raise ValueError("Invalid gameboard(Invalid range(-1 ~ 1)).")
            if int(item) == -1:
                valid_gameboard = False

    return valid_gameboard


def deserialize_gameboard(
    serialized_string: str,
    return_int: bool = False,
) -> List[List[Union[RealBoardCellState, int]]]:
    board = json.loads(serialized_string)
    try:
        validate_gameboard(board)
    except ValueError as error:
        raise ValueError("Failed to deserialize : " + str(error))

    if not return_int:
        board = [
            [RealBoardCellState(item) for item in row]
            for row in board
        ]

    return board


def serialize_gameboard(
    board: List[List[Union[RealBoardCellState, int]]]
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
    select_related: Optional[List[str]] = None,
    **kwargs,
):
    try:
        if select_related is None:
            query = model_class.objects.get(**kwargs)
        else:
            query = model_class.objects.select_related(*select_related).get(**kwargs)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(label)
    except ValidationError:
        raise ValidationError(label)
    return query


async def async_get_from_db(
    model_class: Model,
    label: str,
    select_related: Optional[List[str]] = None,
    **kwargs,
):
    try:
        if select_related is None:
            query = await model_class.objects.aget(**kwargs)
        else:
            query = await model_class.objects.select_related(*select_related).aget(**kwargs)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(label)
    except ValidationError:
        raise ValidationError(label)
    return query


def validate_gameplay(
    board: List[List[Union[int, GameBoardCellState]]]
) -> None:
    if not board or not isinstance(board, list):
        raise ValueError("Invalid gameplay(Invalid type).")

    row_length = len(board[0])

    for row in board:
        if len(row) != row_length:
            raise ValueError("Invalid gameplay(Row length error).")

        for item in row:
            if not isinstance(item, int) and not isinstance(item, GameBoardCellState):
                raise ValueError("Invalid gameplay(Invalid item type).")
            if isinstance(item, int) and not (0 <= item <= 4):
                raise ValueError("Invalid gameplay(Invalid range(0 ~ 4)).")


def deserialize_gameplay(
    serialized_string: str,
    return_int: bool = False,
) -> List[List[Union[GameBoardCellState, int]]]:
    board = json.loads(serialized_string)
    try:
        validate_gameplay(board)
    except ValueError as error:
        raise ValueError("Failed to deserialize : " + str(error))

    if not return_int:
        board = [
            [GameBoardCellState(item) for item in row]
            for row in board
        ]

    return board


def serialize_gameplay(
    board: List[List[Union[GameBoardCellState, int]]]
) -> str:
    try:
        validate_gameplay(board)
    except ValueError as error:
        raise ValueError("Failed to serialize : " + str(error))

    board = [
        [int(item) for item in row]
        for row in board
    ]

    serialize_string = json.dumps(board)

    return serialize_string


def is_uuid4(
    uuid_to_test: str
) -> bool:
    try:
        uuid.UUID(uuid_to_test, version=4)
    except ValueError:
        return False
    return True


async def send_request(
    method_type: str,
    url: str,
    request: Dict[str, Any] = {},
) -> Dict[str, Any]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        if method_type == "POST":
            async with session.post(url, json=request, ssl=False) as resp:
                if resp.status == HTTPStatus.OK:
                    response = await resp.json()
                    response["status_code"] = resp.status
                else:
                    response = {
                        "status_code": resp.status,
                        "response": await resp.text()
                    }
        elif method_type == "GET":
            async with session.get(url, ssl=False) as resp:
                if resp.status == HTTPStatus.OK:
                    response = await resp.json()
                    response["status_code"] = resp.status
                else:
                    response = {
                        "status_code": resp.status,
                        "response": await resp.text()
                    }
        elif method_type == "PUT":
            async with session.put(url, json=request, ssl=False) as resp:
                if resp.status == HTTPStatus.OK:
                    response = await resp.json()
                    response["status_code"] = resp.status
                else:
                    response = {
                        "status_code": resp.status,
                        "response": await resp.text()
                    }
        else:
            raise Exception("invalid method type")
    return response


def convert_board_to_hash(
    array: List[List[Union[GameBoardCellState, int]]],
) -> str:
    string_list = ','.join([''.join(map(str, subarray)) for subarray in array])
    return hashlib.md5(string_list.encode()).hexdigest()


def is_base64(
    base64_to_test: object
) -> bool:
    try:
        if isinstance(base64_to_test, str):
            base64_to_test = base64_to_test.encode()
        elif not isinstance(base64_to_test, bytes):
            return False
        return base64.b64encode(base64.b64decode(base64_to_test)) == base64_to_test
    except Exception:
        return False


LogFunction = TypeVar("LogFunction", bound=Callable[..., Any])


class LogSystem:
    def __init__(
        self,
        module_name: str,
        log_path: str,
        log_level: int = logging.INFO,
    ):
        self._logger = logging.getLogger(module_name)
        self._logger.setLevel(logging.DEBUG)
        self._log_level = log_level

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)

        self._logger.addHandler(ch)

        log_dir = Path(log_path)
        log_dir.mkdir(parents=True, exist_ok=True)

        log_dir.mkdir(parents=True, exist_ok=True)

        ch = logging.FileHandler(f"{log_path}/{module_name}.log")
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        self._logger.addHandler(ch)

    def _log(
        self,
        msg: str,
        log_level: int,
    ) -> None:
        if log_level == logging.INFO:
            self._logger.info(msg)
        elif log_level == logging.ERROR:
            self._logger.error(msg)
        elif log_level == logging.DEBUG:
            self._logger.debug(msg)
        elif log_level == logging.CRITICAL:
            self._logger.critical(msg)
        elif log_level == logging.WARNING:
            self._logger.warning(msg)

    def _decorator(
        self,
        func: LogFunction,
        log_level: int,
        print_args: bool,
    ) -> LogFunction:
        def sync_wrapper(*args, **kwargs) -> Any:
            self._log(f"{func.__name__} begins", log_level=log_level)
            start_time = time.time()
            if print_args:
                kwargs_message = "kwargs: "
                for arg_name, arg_value in kwargs.items():
                    kwargs_message += f"{arg_name}({type(arg_value)}): {arg_value}, "
                self._log(kwargs_message, log_level=log_level)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                self._log(f"Error on {func.__name__}: {e}", logging.ERROR)
                raise
            end_time = time.time()
            self._log(f"{func.__name__} finished", log_level=log_level)
            self._log(f"{func.__name__} excution time: {end_time - start_time: .5f} sec", log_level=log_level)
            return result

        async def async_wrapper(*args, **kwargs) -> Any:
            self._log(f"{func.__name__} begins", log_level=log_level)
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                self._log(f"Error on {func.__name__}: {e}", logging.ERROR)
                raise
            end_time = time.time()
            self._log(f"{func.__name__} finished", log_level=log_level)
            self._log(f"{func.__name__} excution time: {end_time - start_time: .5f} sec", log_level=log_level)
            return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    def log(
        self,
        func_or_msg: Optional[Union[LogFunction, str]] = None,
        *,
        log_level: int = logging.INFO,
        print_args: bool = False,
    ) -> Optional[Union[LogFunction, Callable[[LogFunction], LogFunction]]]:
        if isinstance(func_or_msg, str):
            self._log(func_or_msg, log_level=log_level)
            return
        if func_or_msg:
            return self._decorator(func_or_msg, log_level, print_args)

        def wrapper(func: LogFunction):
            return self._decorator(func, log_level, print_args)

        return wrapper


class Config:
    BLACK_THRESHOLD = 127
    GAME_NOT_START = 0
    LATEST_TURN = -1
    RANDOM_BOARD = 0
    GAME_EXIST = 0
    NEW_GAME_STARTED = 1
    CELL_UNCHANGED = 0
    CELL_APPLIED = 1
    BOARD_GAME_OVER = 2
    GAME_BOARD_CELL_STATE_LOWERBOUND = 0
    GAME_BOARD_CELL_STATE_UPPERBOUND = 4


class LockManager:
    def __init__(
        self,
        lock_key: str,
        max_retries: int = 10,
        retry_interval: float = 0.1
    ):
        self.lock_key = f"lock|{lock_key}"
        self.max_retries = max_retries
        self.retry_interval = retry_interval

    def __enter__(self):
        self.is_locked = False
        for _ in range(self.max_retries):
            if cache.add(self.lock_key, 0):
                self.is_locked = True
                break
            time.sleep(self.retry_interval)

        return self.is_locked
    
    def __exit__(self, type, value, traceback):
        if self.is_locked:
            cache.delete(self.lock_key)

    async def __aenter__(self):
        self.is_locked = False
        for _ in range(self.max_retries):
            if await cache.aadd(self.lock_key, 0):
                self.is_locked = True
                break
            await asyncio.sleep(self.retry_interval)

        return self.is_locked
    
    async def __aexit__(self, type, value, traceback):
        if self.is_locked:
            await cache.adelete(self.lock_key)
