from django.urls import path, include
from . import views

urlpatterns = [
    path('details/', views.details, name='details'),
    path('menu/',views.DrinkMenuView.as_view(), name='drink_menu')
]