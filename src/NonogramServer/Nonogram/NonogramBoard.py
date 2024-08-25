from __future__ import annotations
from NonogramServer.models import NonogramBoard
from NonogramServer.models import Session
from NonogramServer.models import History
from utils import GameBoardCellState
from utils import RealBoardCellState
from utils import deserialize_gameboard
from utils import serialize_gameplay
from utils import deserialize_gameplay
from utils import is_uuid4
from utils import Config
from typing import Union
from typing import Optional
import uuid
import asyncio


class NonogramGameplay:
    def __init__(
        self,
        data: Union[NonogramBoard, Session],
        db_sync: bool = True,
        session_id: Optional[uuid.UUID] = None,
        delayed_save: bool = False,
    ):
        if isinstance(data, Session):
            board_data = data.board_data
            self.unrevealed_counter = data.unrevealed_counter
            self.playboard = deserialize_gameplay(data.board)
            self.session = data
        elif isinstance(data, NonogramBoard):
            board_data = data
            self.unrevealed_counter = data.black_counter
            self.playboard = [
                [int(GameBoardCellState.NOT_SELECTED) for _ in range(data.num_column)]
                for _ in range(data.num_row)
            ]
            if session_id is None:
                session_id = str(uuid.uuid4())
            elif not is_uuid4(session_id):
                raise ValueError("Not uuid4 format")
            self.session = Session(
                session_id=session_id,
                board_data=data,
                board=serialize_gameplay(self.playboard),
                unrevealed_counter=self.unrevealed_counter,
            )
            if db_sync:
                if not delayed_save:
                    self.session.save()
        else:
            raise TypeError("invalid model type.")
        self.board_data = board_data
        self.board_id = board_data.board_id
        self.board = deserialize_gameboard(board_data.board)
        self.num_row = board_data.num_row
        self.num_column = board_data.num_column
        self.black_counter = board_data.black_counter
        self.db_sync = db_sync

    def mark(
        self,
        x: int,
        y: int,
        new_state: Union[GameBoardCellState, int],
        save_db: bool = True,
    ) -> int:
        mark_result = self._mark(x, y, new_state)
        if mark_result != Config.CELL_APPLIED:
            return mark_result
        if save_db and self.db_sync:
            self.session.current_game.save()
            self.session.save()
        else:
            self.db_sync = False
        return mark_result

    async def async_mark(
        self,
        x: int,
        y: int,
        new_state: Union[GameBoardCellState, int],
        save_db: bool = True,
    ) -> int:
        mark_result = self._mark(x, y, new_state)
        if mark_result != Config.CELL_APPLIED:
            return mark_result
        if save_db and self.db_sync:
            await self.session.current_game.asave()
            await self.session.asave()
        else:
            self.db_sync = False
        return mark_result

    def _mark(
        self,
        x: int,
        y: int,
        new_state: Union[GameBoardCellState, int],
    ) -> int:
        if self.unrevealed_counter == 0:
            return Config.BOARD_GAME_OVER
        if not self._markable(x, y, new_state):
            return Config.CELL_UNCHANGED
        self.playboard[x][y] = new_state
        if new_state == GameBoardCellState.REVEALED:
            self.unrevealed_counter -= 1
        self.session.board = serialize_gameplay(self.playboard)
        self.session.unrevealed_counter = self.unrevealed_counter
        self.session.current_game = self._create_history(x, y, new_state)
        return Config.CELL_APPLIED

    def _create_history(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,
    ) -> History:
        current_game = self.session.current_game
        if current_game is None:
            gameplay_id = str(uuid.uuid4())
            new_turn = 1
        else:
            gameplay_id = current_game.gameplay_id
            new_turn = current_game.current_turn + 1
        return History(
            current_session=self.session,
            gameplay_id=gameplay_id,
            current_turn=new_turn,
            type_of_move=new_state,
            x_coord=x,
            y_coord=y,
        )

    def _markable(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,
    ) -> bool:
        if not (0 <= x < self.num_row) or not (0 <= y < self.num_column):
            return False
        current_cell_state = self.playboard[x][y]
        current_cell = self.board[x][y]
        if current_cell_state == GameBoardCellState.REVEALED or current_cell_state == GameBoardCellState.MARK_WRONG:
            return False
        if new_state == GameBoardCellState.REVEALED:
            return current_cell == RealBoardCellState.BLACK
        elif new_state == GameBoardCellState.MARK_WRONG:
            return current_cell == RealBoardCellState.WHITE
        return current_cell_state != new_state

    def save(self) -> None:
        if self.db_sync:
            self.session.save()

    async def asave(self) -> None:
        if self.db_sync:
            await self.session.asave()

    def reset(
        self,
        db_sync: bool = True,
    ):
        self._reset()
        if self.db_sync:
            self.db_sync = db_sync
            if db_sync:
                for history in History.objects.filter(current_session=self.session):
                    history.current_session = None
                    history.save()

    async def async_reset(
        self,
        db_sync: bool = True,
    ):
        self._reset()
        if self.db_sync:
            self.db_sync = db_sync
            if db_sync:
                # TODO: 비동기 task queue를 사용해서 업데이트하는 로직으로 변경
                coroutine = []
                async for history in History.objects.filter(current_session=self.session):
                    history.current_session = None
                    coroutine.append(asyncio.create_task(history.asave()))
                await asyncio.gather(*coroutine)

    def _reset(self):
        self.unrevealed_counter = self.black_counter
        self.playboard = [
            [int(GameBoardCellState.NOT_SELECTED) for y in range(self.num_column)]
            for x in range(self.num_row)
        ]
        self.session.board = serialize_gameplay(self.playboard)
        self.session.unrevealed_counter = self.unrevealed_counter
        self.session.current_game = None
