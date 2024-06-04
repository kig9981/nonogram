"""
URL configuration for ApiServer project.

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
from .views.GetNonogramBoard import GetNonogramBoard
from .views.GetNonogramPlay import GetNonogramPlay
from .views.Synchronize import Synchronize
from .views.MakeMove import MakeMove
from .views.CreateNewSession import CreateNewSession
from .views.CreateNewGame import CreateNewGame
from .views.Healthcheck import HealthCheck

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthcheck/', HealthCheck.as_view(), name="healthcheck"),
    path("sessions/<str:session_id>/board/", GetNonogramBoard.as_view(), name="get_nonogram_board"),
    path("sessions/<str:session_id>/play/", GetNonogramPlay.as_view(), name="get_nonogram_play"),
    path("sessions/<str:session_id>/sync/", Synchronize.as_view(), name="synchronize"),
    path("sessions/<str:session_id>/move/", MakeMove.as_view(), name="make_move"),
    path("sessions/", CreateNewSession.as_view(), name="create_new_session"),
    path("sessions/<str:session_id>/game/", CreateNewGame.as_view(), name="create_new_game"),
]
