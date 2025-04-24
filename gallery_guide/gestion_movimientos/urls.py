from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_movimiento, name='lista_movimientos'),
    path('<slug:movement_slug>/obras/', views.obras_movimiento, name='obras_movimiento'),
    path('api/obras-movimiento/<slug:movement_slug>/', views.api_obras_movimiento, name='api_obras_movimiento'),
]
