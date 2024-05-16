from __future__ import annotations
from NonogramServer.models import NonogramBoard
from NonogramServer.models import Session
from NonogramServer.models import History
from utils import GameBoardCellState
from utils import RealBoardCellState
from utils import serialize_gameplay
from utils import deserialize_gameplay
from typing import Union
import uuid


class NonogramGameplay:
    def __init__(
        self,
        data: Union[NonogramBoard, Session],
    ):
        if isinstance(data, Session):
            self.session = data
            self.board_data = data.board_data
            self.board_id = data.board_data.board_id
            self.board = data.board_data.board
            self.num_row = data.board_data.num_row
            self.num_column = data.board_data.num_column
            self.black_counter = data.board_data.black_counter
            self.unrevealed_counter = data.unrevealed_counter
            self.playboard = deserialize_gameplay(data.board)
        else:
            self.board_data = data
            self.board_id = data.board_id
            self.board = data.board
            self.num_row = data.num_row
            self.num_column = data.num_column
            self.black_counter = data.black_counter
            self.unrevealed_counter = data.black_counter
            self.playboard = [
                [int(GameBoardCellState.NOT_SELECTED) for y in range(self.num_column)]
                for x in range(self.num_row)
            ]
            self.session = Session(
                session_id=str(uuid.uuid4()),
                board_data=data,
                board=serialize_gameplay(self.playboard),
                unrevealed_counter=self.unrevealed_counter,
            )

    def mark(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,
        save_db: bool = False,

    ) -> bool:
        if not self._markable(x, y, new_state):
            return False
        self.playboard[x][y] = new_state
        if new_state == GameBoardCellState.REVEALED:
            self.unrevealed_counter -= 1
        self.session.board = serialize_gameplay(self.playboard)
        self.session.unrevealed_counter = self.unrevealed_counter
        self.session.current_game = self._create_history(x, y, new_state)
        if save_db:
            self.session.current_game.save()
            self.session.save()
        return True

    async def async_mark(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,
        save_db: bool = True,

    ) -> bool:
        if not self.mark(x, y, new_state):
            return False
        if save_db:
            await self.session.current_game.asave()
            await self.session.asave()
        return True

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
        if current_cell_state == GameBoardCellState.REVEALED:
            return False
        if new_state == GameBoardCellState.REVEALED:
            if current_cell == RealBoardCellState.BLACK:
                return True
            return False
        return current_cell_state != new_state

    def save(self) -> None:
        self.session.save()

    async def asave(self) -> None:
        await self.session.asave()
