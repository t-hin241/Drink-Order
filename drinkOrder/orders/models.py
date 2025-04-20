from django.db import models
from drinks.models import Drink
from users.models import CustomUser
# Create your models here.

class Order(models.Model):
    status_choices = [
        ('pending', 'Pending'),
        ('served', 'Served'),
    ]
    created_on = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(choices=status_choices, default='pending')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(Drink, through='OrderItem')
    
    def __str__(self):
        return f"Order{self.id} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.drink.name} (x{self.quantity})"