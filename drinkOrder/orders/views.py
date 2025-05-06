from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Order, OrderItem
from drinks.models import Drink
from django.urls import reverse
import logging

logger = logging.getLogger('django')

class OrderListView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_bartender
    def get(self, request):
        pending_orders = Order.objects.filter(status='pending').order_by('created_on')
        return render(request, 'orders/order_list.html', {'orders': pending_orders})

class ServeOrderView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_bartender
    def post(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id, status='pending')
            order.status = 'served'
            order.save()
            return redirect(reverse('orders:order_list'))
        except Exception as e:
            logger.error(f"ServeOrderView error: {str(e)}")
            return redirect(reverse('orders:order_list'))

class PlaceOrderView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_customer
    def get(self, request):
        drinks = Drink.objects.all().order_by('name')
        return render(request, 'orders/order_form.html', {'drinks': drinks})

    def post(self, request):
        drinks = Drink.objects.all()
        total_price = 0
        order_items = []

        # Process quantities from form
        for drink in drinks:
            quantity = request.POST.get(f'quantity_{drink.id}', '0')
            try:
                quantity = int(quantity)
                if quantity > 0:
                    total_price += drink.price * quantity
                    order_items.append((drink, quantity))
            except ValueError:
                logger.error(f"Invalid quantity for drink {drink.id}: {quantity}")
                continue

        if not order_items:
            return render(request, 'orders/order_form.html', {
                'drinks': drinks,
                'error': 'Please select at least one drink.'
            })

        # Create order
        try:
            order = Order.objects.create(
                total_price=total_price,
                status='pending',
                customer=request.user
            )
            for drink, quantity in order_items:
                OrderItem.objects.create(
                    order=order,
                    drink=drink,
                    quantity=quantity
                )
            return render(request, 'orders/order_confirmation.html', {'order': order})
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return render(request, 'orders/order_form.html', {
                'drinks': drinks,
                'error': 'Failed to place order. Please try again.'
            })


class CustomerOrderView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_customer
    def get(self, request):
        orders = Order.objects.filter(customer=request.user).order_by('-created_on')
        return render(request, 'orders/customer_order_list.html', {'orders': orders})

class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_customer
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, customer=request.user, status='pending')
        drinks = Drink.objects.all().order_by('name')
        # Add current quantities to drinks
        current_items = {item.drink.id: item.quantity for item in order.orderitem_set.all()}
        for drink in drinks:
            drink.current_quantity = current_items.get(drink.id, 0)
        return render(request, 'orders/order_update.html', {
            'order': order,
            'drinks': drinks,
        })

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, customer=request.user, status='pending')
        if request.POST.get('cancel') == 'true':
            try:
                order.delete()
                return redirect('orders:customer_order_list')
            except Exception as e:
                logger.error(f"Error canceling order {order_id}: {str(e)}")
                orders = Order.objects.filter(customer=request.user).order_by('-created_on')
                return render(request, 'orders/customer_order_list.html', {
                    'orders': orders,
                    'error': 'Failed to cancel order. Please try again.'
                })

        drinks = Drink.objects.all()
        total_price = 0
        order_items = []

        for drink in drinks:
            quantity = request.POST.get(f'quantity_{drink.id}', '0')
            try:
                quantity = int(quantity)
                if quantity > 0:
                    total_price += drink.price * quantity
                    order_items.append((drink, quantity))
            except ValueError:
                logger.error(f"Invalid quantity for drink {drink.id}: {quantity}")
                continue

        if not order_items:
            return render(request, 'orders/order_update.html', {
                'order': order,
                'drinks': drinks,
                'error': 'Please select at least one drink.'
            })

        try:
            # Update order
            order.total_price = total_price
            order.save()
            # Clear existing items and add new ones
            order.orderitem_set.all().delete()
            for drink, quantity in order_items:
                OrderItem.objects.create(
                    order=order,
                    drink=drink,
                    quantity=quantity
                )
            return redirect('orders:customer_order_list')
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {str(e)}")
            return render(request, 'orders/order_update.html', {
                'order': order,
                'drinks': drinks,
                'error': 'Failed to update order. Please try again.'
            })