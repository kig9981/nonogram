import uuid
from django.db import models
from django.core.exceptions import ValidationError
from utils import deserialize_gameboard


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
    gameplay = models.ForeignKey("Game", on_delete=models.CASCADE, db_index=True)
    occured_at = models.DateTimeField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    current_turn = models.IntegerField()
    type_of_move = models.IntegerField(choices=MoveType)
    x_coord = models.IntegerField()
    y_coord = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["gameplay", "current_turn"]),
            models.Index(fields=["current_turn"]),
        ]


class Game(models.Model):
    current_session = models.ForeignKey("Session", on_delete=models.SET_NULL, null=True, db_index=True)
    gameplay_id = models.UUIDField(validators=[validate_uuid4], editable=False)
    board_data = models.ForeignKey("NonogramBoard", on_delete=models.SET_DEFAULT, null=True, default=None)
    board = models.TextField(null=True, default=None)
    unrevealed_counter = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["current_session", "active"]),
        ]


class Session(models.Model):
    session_id = models.UUIDField(primary_key=True, validators=[validate_uuid4], editable=False, unique=True)
    latest_update_time = models.DateTimeField(auto_now=True)
    client_session_key = models.TextField()

    def save(self, *args, **kwargs):
        if kwargs.has_key('update_fields'):
            kwargs = list(set(list(kwargs['update_fields']) + ['latest_update_time']))
        else:
            kwargs['update_fields'] = ['latest_update_time']
        return super().save(*args, **kwargs)