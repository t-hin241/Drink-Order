from django.urls import path, include
from .views import DrinkMenuView, DrinkDetailView, ReviewCreateView, ReviewEditView, ReviewDeleteView

app_name = 'drinks'

urlpatterns = [
    path('', DrinkMenuView.as_view(), name='drink_menu'),
    path('<int:drink_id>/', DrinkDetailView.as_view(), name='drink_detail'),
    path('<int:drink_id>/review/', ReviewCreateView.as_view(), name='review_create'),
    path('<int:drink_id>/review/<int:review_id>/edit/', ReviewEditView.as_view(), name='review_edit'),
    path('<int:drink_id>/review/<int:review_id>/delete/', ReviewDeleteView.as_view(), name='review_delete'),    
]