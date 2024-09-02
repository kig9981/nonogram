from __future__ import annotations
from NonogramServer.models import NonogramBoard
from NonogramServer.models import Game
from NonogramServer.models import Session
from NonogramServer.models import History
from NonogramServer.views.configure import LOG_PATH
from utils import GameBoardCellState
from utils import RealBoardCellState
from utils import deserialize_gameboard
from utils import serialize_gameplay
from utils import deserialize_gameplay
from utils import is_uuid4
from utils import Config
from utils import LogSystem
from typing import Union
from typing import Optional
from typing import Tuple
import uuid
import asyncio
from datetime import datetime


class NonogramGameplay:
    logger = LogSystem(
        module_name=__name__,
        log_path=LOG_PATH,
    )

    def __init__(
        self,
        data: Union[NonogramBoard, Game],
        db_sync: bool = True,
        session: Optional[Session] = None,
        delayed_save: bool = False,
    ):
        if isinstance(data, Game):
            board_data = data.board_data
            self.unrevealed_counter = data.unrevealed_counter
            self.playboard = deserialize_gameplay(data.board)
            self.game = data
        elif isinstance(data, NonogramBoard):
            board_data = data
            self.unrevealed_counter = data.black_counter
            self.playboard = [
                [int(GameBoardCellState.NOT_SELECTED) for _ in range(data.num_column)]
                for _ in range(data.num_row)
            ]
            self.game = Game(
                current_session=session,
                gameplay_id=str(uuid.uuid4()),
                board_data=data,
                board=serialize_gameplay(self.playboard),
                unrevealed_counter=self.unrevealed_counter,
            )
            if db_sync:
                if not delayed_save:
                    self.game.save()
        else:
            raise TypeError("invalid model type.")
        self.board_data = board_data
        self.board_id = board_data.board_id
        self.board = deserialize_gameboard(board_data.board)
        self.num_row = board_data.num_row
        self.num_column = board_data.num_column
        self.black_counter = board_data.black_counter
        self.db_sync = db_sync

    @logger.log
    def mark(
        self,
        x: int,
        y: int,
        new_state: Union[GameBoardCellState, int],
        occured_at: datetime = datetime.now(),
        save_db: bool = True,
    ) -> int:
        mark_result = self._mark(x, y, new_state)
        if mark_result != Config.CELL_APPLIED:
            return mark_result
        if save_db and self.db_sync:
            new_turn = History.objects.filter(
                gameplay=self.game,
            ).count()
            self._create_history(x, y, new_state, new_turn, occured_at).save()
            self.game.save()
            if self.game.current_session:
                self.game.current_session.save()
        else:
            self.db_sync = False
        return mark_result

    @logger.log
    async def async_mark(
        self,
        x: int,
        y: int,
        new_state: Union[GameBoardCellState, int],
        occured_at: datetime = datetime.now(),
        save_db: bool = True,
    ) -> int:
        mark_result = self._mark(x, y, new_state)
        if mark_result != Config.CELL_APPLIED:
            return mark_result
        if save_db and self.db_sync:
            latest_turn = await History.objects.filter(
                gameplay=self.game,
            ).acount()
            new_turn = latest_turn + 1
            await self._create_history(x, y, new_state, new_turn, occured_at).asave()
            await self.game.asave()
            if self.game.current_session:
                await self.game.current_session.asave()
        else:
            self.db_sync = False
        return mark_result

    @logger.log
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
        self.game.board = serialize_gameplay(self.playboard)
        self.game.unrevealed_counter = self.unrevealed_counter
        return Config.CELL_APPLIED

    @logger.log
    def _create_history(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,
        new_turn: int,
        occured_at: datetime,
    ) -> History:
        current_game = self.game
        return History(
            gameplay=current_game,
            occured_at=occured_at,
            current_turn=new_turn,
            type_of_move=new_state,
            x_coord=x,
            y_coord=y,
        )

    @logger.log
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

    @logger.log
    def save(self) -> None:
        if self.db_sync:
            self.game.save()

    @logger.log
    async def asave(self) -> None:
        if self.db_sync:
            await self.game.asave()

    @logger.log
    def reset(
        self,
        db_sync: bool = True,
    ):
        self._reset()
        if self.db_sync:
            self.db_sync = db_sync
            if db_sync:
                self.game.save()

    @logger.log
    async def async_reset(
        self,
        db_sync: bool = True,
    ):
        self._reset()
        if self.db_sync:
            self.db_sync = db_sync
            if db_sync:
                await self.game.asave()

    @logger.log
    def _reset(self):
        self.unrevealed_counter = self.black_counter
        self.playboard = [
            [int(GameBoardCellState.NOT_SELECTED) for y in range(self.num_column)]
            for x in range(self.num_row)
        ]
        self.game = Game(
            current_session=self.game.session,
            gameplay_id=str(uuid.uuid4()),
            board_data=self.board_data,
            board=serialize_gameplay(self.playboard),
            unrevealed_counter=self.unrevealed_counter,
        )
