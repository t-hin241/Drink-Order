from django.urls import path, include
from .views import OrderListView, PlaceOrderView, ServeOrderView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('place-order/', PlaceOrderView.as_view(), name='place-order'),
    path('serve/<int:order_id>/', ServeOrderView.as_view(), name='serve_order'),
]