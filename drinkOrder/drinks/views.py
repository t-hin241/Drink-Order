from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import Drink, Category

class DrinkMenuView(View):
    def get(self, request):
        drinks = Drink.objects.all().order_by('name')
        categories = Category.objects.all()
        return render(request, 'drinks/drink_menu.html', {
            'drinks': drinks,
            'categories': categories,
        })

class DrinkDetailView(View):
    def get(self, request, drink_id):
        drink = get_object_or_404(Drink, id=drink_id)
        return render(request, 'drinks/drink_detail.html', {'drink': drink})