# coding=utf-8
# time :2022/8/11
from django.urls import path

from . import views

urlpatterns = [
    path('reg', views.reg_view),
    path('login', views.login_view),
    path('logout', views.logout_view),
]