import uuid
from django.db import models
from django.core.exceptions import ValidationError
from utils import deserialize_gameboard
from utils import deserialize_gameplay
from utils import serialize_gameplay
from utils import GameBoardCellState
from utils import RealBoardCellState


class MoveType(models.IntegerChoices):
    NOT_SELECTED = 0
    REVEALED = 1
    MARK_X = 2
    MARK_QUESTION = 3


def validate_uuid4(value):
    try:
        val = uuid.UUID(str(value))
        if val.version != 4:
            raise ValidationError("This field requires version 4 UUID.")
    except ValueError:
        raise ValidationError("Invalid UUID format.")


# Create your models here.
class NonogramBoard(models.Model):
    board_id = models.UUIDField(validators=[validate_uuid4], editable=False, unique=True)
    board = models.TextField(null=True)
    num_row = models.IntegerField(default=5)
    num_column = models.IntegerField(default=5)
    black_counter = models.IntegerField()
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
    current_session = models.ForeignKey("Session", on_delete=models.SET_NULL, null=True)
    gameplay_id = models.UUIDField(validators=[validate_uuid4], editable=False)
    current_turn = models.IntegerField()
    type_of_move = models.IntegerField(choices=MoveType)
    x_coord = models.IntegerField()
    y_coord = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['gameplay_id', 'current_turn'],
                name="(game, turn) tuple"
            ),
        ]


class Session(models.Model):
    session_id = models.UUIDField(primary_key=True, validators=[validate_uuid4], editable=False, unique=True)
    current_game = models.ForeignKey("History", on_delete=models.SET_DEFAULT, null=True, default=None)
    board_data = models.ForeignKey("NonogramBoard", on_delete=models.SET_DEFAULT, null=True, default=None)
    board = models.TextField(null=True, default=None)
    unrevealed_counter = models.IntegerField(default=0)

    def mark(
        self,
        x: int,
        y: int,
        new_state: GameBoardCellState,
    ) -> bool:
        board_data = self.board_data
        current_game = self.current_game

        if board_data is None or self.unrevealed_counter == 0:
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
            if new_state == GameBoardCellState.REVEALED:
                self.unrevealed_counter -= 1
            if current_game is None:
                gameplay_id = uuid.uuid4()
                current_turn = 1
            else:
                gameplay_id = current_game.gameplay_id
                current_turn = current_game.current_turn + 1
            new_history = History(
                current_session=self,
                gameplay_id=gameplay_id,
                current_turn=current_turn,
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

        if board_data is None or self.unrevealed_counter == 0:
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
            if new_state == GameBoardCellState.REVEALED:
                self.unrevealed_counter -= 1
            if current_game is None:
                gameplay_id = uuid.uuid4()
                current_turn = 1
            else:
                gameplay_id = current_game.gameplay_id
                current_turn = current_game.current_turn + 1
            new_history = History(
                current_session=self,
                gameplay_id=gameplay_id,
                current_turn=current_turn,
                type_of_move=int(new_state),
                x_coord=x,
                y_coord=y,
            )
            await new_history.asave()
            self.current_game = new_history
            self.board = serialize_gameplay(play)
            await self.asave()
        return changed
