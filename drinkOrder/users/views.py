from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from .models import CustomUser
from drinks.models import Drink
from orders.models import Order
from django.utils import timezone
from django.db.models import Sum
from django.urls import reverse_lazy
import logging

logger = logging.getLogger('django')
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')
class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            return redirect('drinks:drink_menu')  # Redirect to drink menu
        return render(request, 'users/register.html', {'form': form})

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = CustomUserUpdateForm(instance=request.user)
        return render(request, 'users/profile.html', {'form': form})

    def post(self, request):
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
        return render(request, 'users/profile.html', {'form': form})
    

### Bartender features ###
class CustomerListView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_bartender

    def get(self, request):
        customers = CustomUser.objects.filter(is_customer=True, is_superuser=False).order_by('full_name', 'username')
        logger.info(f"Bartender {request.user.username} viewed customer list")
        return render(request, 'users/customer_list.html', {
            'customers': customers,
        })

class CustomerProfileView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_bartender

    def get(self, request, customer_id):
        customer = get_object_or_404(CustomUser, id=customer_id, is_customer=True)
        if not customer.share_profile:
            logger.warning(f"Bartender {request.user.username} attempted to view non-shared profile of {customer.username}")
            return render(request, 'users/customer_profile.html', {
                'error': "This customer has not opted in to share their profile."
            })

        # Favorite drinks: Top 3 drinks by quantity ordered
        favorite_drinks = Drink.objects.filter(
            orderitem__order__customer=customer
        ).annotate(
            total_quantity=Sum('orderitem__quantity')
        ).order_by('-total_quantity')[:3]

        # Visit frequency: Orders in last 30 days
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        visit_count = Order.objects.filter(
            customer=customer,
            created_on__gte=thirty_days_ago
        ).count()

        logger.info(f"Bartender {request.user.username} viewed profile of {customer.username}")
        return render(request, 'users/customer_profile.html', {
            'customer': customer,
            'favorite_drinks': favorite_drinks,
            'visit_count': visit_count,
        })    