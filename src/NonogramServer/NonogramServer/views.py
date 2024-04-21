from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from .models import NonogramBoard

# Create your views here.
def get_nonogram_board(request: HttpRequest):
    # NonogramBoard.objects.get(pk=-1)
    return HttpResponse("get_nonogram_board")
