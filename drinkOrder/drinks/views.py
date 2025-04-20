from django.shortcuts import render
from django.views import View
from .models import Drink

# Create your views here.
def details():
    return

class DrinkMenuView(View):
    def get(self, request):
        drinks = Drink.objects.all()
        return render(request, 'drink_menu.html', {'drinks': drinks})