from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

class Drink (models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
