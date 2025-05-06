from django.db import models
from users.models import CustomUser
from drinks.models import Drink

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('served', 'Served'),
    ]
    created_on = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField(Drink, through='OrderItem')

    def __str__(self):
        return f"Order {self.id} ({self.status})"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.drink.name} (x{self.quantity})"