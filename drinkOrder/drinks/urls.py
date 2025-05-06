from django.urls import path, include
from .views import DrinkMenuView, DrinkDetailView

app_name = 'drinks'

urlpatterns = [
    path('', DrinkMenuView.as_view(), name='drink_menu'),
    path('<int:drink_id>/', DrinkDetailView.as_view(), name='drink_detail'),
]