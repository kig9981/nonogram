from django.db import models
from django.core.exceptions import ValidationError
from Nonogram.utils import deserialize_gameboard
from Nonogram.utils import deserialize_gameplay
from Nonogram.utils import serialize_gameplay
from Nonogram.utils import GameBoardCellState
from Nonogram.utils import RealBoardCellState


class MoveType(models.IntegerChoices):
    NOT_SELECTED = 0
    REVEALED = 1
    MARK_X = 2
    MARK_QUESTION = 3


# Create your models here.
class NonogramBoard(models.Model):
    board_id = models.IntegerField(primary_key=True)
    board = models.TextField(null=True)
    num_row = models.IntegerField(default=5)
    num_column = models.IntegerField(default=5)
    theme = models.CharField(max_length=20, default="")

    def clean(self):
        super().clean()
        try:
            board = deserialize_gameboard(self.board)
        except ValueError as error:
            raise ValidationError(f"Invalid board data ({error})")
        row, column = len(board), len(board[0])

        if row != self.num_row or column != self.num_column:
            raise ValidationError("Mismatch between provided row and column counts and actual board data")


class History(models.Model):
    current_session = models.ForeignKey("Session", on_delete=models.CASCADE)
    gameplay_id = models.IntegerField()
    current_turn = models.IntegerField()
    type_of_move = models.IntegerField(choices=MoveType)
    x_coord = models.IntegerField()
    y_coord = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['current_session', 'gameplay_id', 'current_turn'],
                name="(session, game, turn) tuple"
            ),
        ]


class Session(models.Model):
    session_id = models.IntegerField(primary_key=True)
    current_game = models.ForeignKey("History", on_delete=models.SET_DEFAULT, null=True, default=None)
    board_data = models.ForeignKey("NonogramBoard", on_delete=models.SET_DEFAULT, null=True, default=None)
    board = models.TextField(null=True)

    def mark(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,
    ) -> bool:
        board_data = self.board_data
        current_game = self.current_game

        if current_game is None or board_data is None:
            return False

        num_row = board_data.num_row
        num_column = board_data.num_column

        if not (0 <= x < num_row) or not (0 <= y < num_column):
            return False

        board = deserialize_gameboard(board_data.board)
        play = deserialize_gameplay(self.board)

        current_cell_state = play[x][y]
        current_cell = board[x][y]
        changed = False

        if current_cell_state == GameBoardCellState.REVEALED:
            return False
        if new_state == GameBoardCellState.REVEALED:
            if current_cell == RealBoardCellState.BLACK:
                changed = True
        elif current_cell_state != new_state:
            changed = True

        if changed:
            play[x][y] = new_state
            new_history = History(
                current_session=self,
                gameplay_id=current_game.gameplay_id,
                current_turn=current_game.current_turn + 1,
                type_of_move=int(new_state),
                x_coord=x,
                y_coord=y,
            )
            new_history.save()
            self.current_game = new_history
            self.board = serialize_gameplay(play)
            self.save()
        return changed
    
    async def async_mark(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,
    ) -> bool:
        board_data = self.board_data
        current_game = self.current_game

        if current_game is None or board_data is None:
            return False

        num_row = board_data.num_row
        num_column = board_data.num_column

        if not (0 <= x < num_row) or not (0 <= y < num_column):
            return False

        board = deserialize_gameboard(board_data.board)
        play = deserialize_gameplay(self.board)

        current_cell_state = play[x][y]
        current_cell = board[x][y]
        changed = False

        if current_cell_state == GameBoardCellState.REVEALED:
            return False
        if new_state == GameBoardCellState.REVEALED:
            if current_cell == RealBoardCellState.BLACK:
                changed = True
        elif current_cell_state != new_state:
            changed = True

        if changed:
            play[x][y] = new_state
            new_history = History(
                current_session=self,
                gameplay_id=current_game.gameplay_id,
                current_turn=current_game.current_turn + 1,
                type_of_move=int(new_state),
                x_coord=x,
                y_coord=y,
            )
            await new_history.asave()
            self.current_game = new_history
            self.board = serialize_gameplay(play)
            await self.asave()
        return changed
