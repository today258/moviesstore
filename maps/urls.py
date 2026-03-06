from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='maps.index'),
    path('api/<str:iso2>/', views.country_movies, name='maps.country_movies'),
]
