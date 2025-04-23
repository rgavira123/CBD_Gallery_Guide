from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_autores, name='lista_autores'),
    path('<slug:author_slug>/obras/', views.obras_autor, name='obras_autor'),
    path('api/obras-autor/<slug:author_slug>/', views.api_obras_autor, name='api_obras_autor'),
]
