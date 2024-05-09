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
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("get_nonogram_board/", views.get_nonogram_board, name="get_nonogram_board"),
    path("get_nonogram_play/", views.get_nonogram_play, name="get_nonogram_play"),
    path("synchronize/", views.synchronize, name="synchronize"),
    path("make_move/", views.make_move, name="make_move"),
    path("create_new_session/", views.create_new_session, name="create_new_session"),
    path("create_new_game/", views.create_new_game, name="create_new_game"),
]
