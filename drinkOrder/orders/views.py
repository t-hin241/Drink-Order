from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from .models import Order, OrderItem
from drinks.models import Drink

class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        # Retrieve only pending orders
        pending_orders = Order.objects.filter(status='pending').order_by('created_on')
        return render(request, 'orders/order_list.html', {'orders': pending_orders})

# Function-based equivalent:
# from django.contrib.auth.decorators import login_required
# @login_required
# def order_list_view(request):
#     pending_orders = Order.objects.filter(status='pending').order_by('created_on')
#     return render(request, 'orders/order_list.html', {'orders': pending_orders})

class ServeOrderView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        # Retrieve the order or return 404 if not found
        order = get_object_or_404(Order, id=order_id, status='pending')
        # Update status to served
        order.status = 'served'
        order.save()
        # Redirect to the order list
        return redirect(reverse('orders:order_list'))


class PlaceOrderView(View):
    def post(self, request):
        selected_drinks = request.POST.getlist('drinks[]')
        order = Order.objects.create(total_price=0, status='pending')
        total_price = 0
        for drink_id in selected_drinks:
            drink = Drink.objects.get(id=drink_id)
            quantity = int(request.POST.get(f'quantity_{drink_id}', 1))
            OrderItem.objects.create(order=order, drink=drink, quantity=quantity)
            total_price += drink.price * quantity
        order.total_price = total_price
        order.save()
        return render(request, 'order_confirmation.html', {'order': order})
    


