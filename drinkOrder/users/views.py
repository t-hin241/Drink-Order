from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.urls import reverse_lazy

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