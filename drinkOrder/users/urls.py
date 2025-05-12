from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RegisterView, ProfileView, CustomerListView, CustomerProfileView

app_name = 'users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('profile/<int:customer_id>/', CustomerProfileView.as_view(), name='customer_profile'),
]