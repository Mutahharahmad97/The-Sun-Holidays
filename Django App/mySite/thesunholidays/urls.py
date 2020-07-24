from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('DetailApi', views.DetailApi, name="DetailApi"),
]
