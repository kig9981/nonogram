from django.db import models
from django.core.exceptions import ValidationError
from Nonogram.utils import deserialize_gameboard


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


class Session(models.Model):
    session_id = models.IntegerField(primary_key=True)
    current_game_id = models.ForeignKey("History", on_delete=models.CASCADE, null=True)
    board_id = models.ForeignKey("NonogramBoard", on_delete=models.CASCADE, null=True)
    revealed = models.TextField(null=True)
    mark_x = models.TextField(null=True)
    mark_question = models.TextField(null=True)


class History(models.Model):
    session_id = models.ForeignKey("Session", on_delete=models.CASCADE)
    gameplay_id = models.IntegerField()
    current_turn = models.IntegerField()
    type_of_move = models.IntegerField(choices=MoveType)
    x_coord = models.IntegerField()
    y_coord = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session_id', 'gameplay_id', 'current_turn'],
                name="(session, game, turn) tuple"
            ),
        ]
