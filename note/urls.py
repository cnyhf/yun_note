# coding=utf-8
# time :2022/8/12
from django.urls import path

from . import views

urlpatterns = [
    path('add', views.add_note)
]