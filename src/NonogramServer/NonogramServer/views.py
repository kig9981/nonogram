from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse

# Create your views here.
def get_nonogram_board(request: HttpRequest):
    return HttpResponse("get_nonogram_board")