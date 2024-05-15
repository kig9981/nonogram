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
from . import view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("get_nonogram_board/", GetNonogramBoard.as_view(), name="get_nonogram_board"),
    path("get_nonogram_play/", GetNonogramPlay.as_view(), name="get_nonogram_play"),
    path("synchronize/", view.synchronize, name="synchronize"),
    path("make_move/", view.make_move, name="make_move"),
    path("create_new_session/", view.create_new_session, name="create_new_session"),
    path("create_new_game/", view.create_new_game, name="create_new_game"),
]
