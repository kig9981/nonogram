from django.db import models

# Create your models here.
class NonogramBoard(models.Model):
    board_id = models.IntegerField(primary_key=True)
    board = models.TextField(null=True)


class Session(models.Model):
    session_id = models.IntegerField(primary_key=True)
    board_id = models.ForeignKey(NonogramBoard, on_delete=models.CASCADE)
    revealed = models.TextField(null=True)
    mark_x = models.TextField(null=True)
    mark_question = models.TextField(null=True)