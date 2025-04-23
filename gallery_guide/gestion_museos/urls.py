"""
URL configuration for gallery_guide project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from gestion_museos import views

urlpatterns = [
    path('', views.listar_museos, name='listar_museos'),
    path('<slug:museum_slug>/', views.museum_graph_view, name='museum_graph'),
    path('<slug:museum_slug>/sala/<slug:room_slug>/', views.room_artworks_view, name='room_artworks'),
    path('artwork/<slug:artwork_slug>/', views.artwork_detail, name='artwork_detail'),
]
