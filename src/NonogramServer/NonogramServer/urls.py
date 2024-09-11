"""
URL configuration for NonogramServer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from .views.GetNonogramBoard import GetNonogramBoard
from .views.GetNonogramPlay import GetNonogramPlay
from .views.SetCellState import SetCellState
from .views.CreateNewSession import CreateNewSession
from .views.HandleGame import HandleGame
from .views.AddNonogramBoard import AddNonogramBoard
from .views.Healthcheck import HealthCheck

urlpatterns = [
    path('admin', admin.site.urls),
    path('', include('django_prometheus.urls')),
    path('healthcheck', HealthCheck.as_view(), name="healthcheck"),
    path("sessions", CreateNewSession.as_view(), name="create_new_session"),
    path("sessions/<str:session_id>", HandleGame.as_view(), name="create_new_game/get_session_board"),
    path("sessions/<str:session_id>/turn/<str:game_turn_str>", GetNonogramPlay.as_view(), name="get_nonogram_play"),
    path("sessions/<str:session_id>/move", SetCellState.as_view(), name="set_cell_state"),
    path("nonogram", AddNonogramBoard.as_view(), name="add_nonogram_board"),
    path("nonogram/<str:board_id>", GetNonogramBoard.as_view(), name="get_nonogram_board"),
]
