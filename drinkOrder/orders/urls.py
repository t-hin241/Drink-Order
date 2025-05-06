from django.urls import path, include
from .views import OrderListView, ServeOrderView, PlaceOrderView, CustomerOrderView, OrderUpdateView

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('serve/<int:order_id>/', ServeOrderView.as_view(), name='serve_order'),
    path('place/', PlaceOrderView.as_view(), name='place_order'),
    path('my-orders/', CustomerOrderView.as_view(), name='customer_order_list'),
    path('update/<int:order_id>/', OrderUpdateView.as_view(), name='order_update'),
]