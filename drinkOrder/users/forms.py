from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address')

class CustomUserUpdateForm(UserChangeForm):
    password = None  # Remove password field from form

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address')