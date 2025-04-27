from django.contrib import admin
from django.urls import path
from gestion_rutas import views
app_name = "gestion_rutas"

urlpatterns = [
    path('crear/<slug:museum_slug>/', views.create_route_view, name="create_route"),
    path('generar/', views.generate_route_view, name="generate_route"),
    path('mis_rutas/', views.mis_rutas_view, name="mis_rutas"),
    path('ver/<slug:route_slug>/', views.ruta_grafo_view, name="ver_ruta"),
    path('explorar/', views.explorar_rutas_view, name="explorar_rutas"),
    path('toggle-visibility/<slug:route_slug>/', views.toggle_route_visibility, name="toggle_visibility"),
]