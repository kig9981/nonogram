from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from .models import NonogramBoard


# Create your views here.
def get_nonogram_board(request: HttpRequest):
    # NonogramBoard.objects.get(pk=-1)
    if request.method == "GET":
        return HttpResponse("get_nonogram_board(get)")
    else:
        return HttpResponse("get_nonogram_board(post)")


def set_cell_status(request: HttpRequest):
    if request.method == "GET":
        return HttpResponse("set_cell_status(get)")
    else:
        return HttpResponse("set_cell_status(post)")
