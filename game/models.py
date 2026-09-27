from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Categories"
       
    def __str__(self):
        return self.name    

class Game(models.Model):
    name = models.CharField(max_length=35)
    description = models.CharField(max_length=300)
    categories = models.ManyToManyField(Category)
    image = models.ImageField()
    release = models.DateField(blank=True, null=True)
    prev_price = models.DecimalField(decimal_places=2, max_digits=5)
    price = models.DecimalField(decimal_places=2, max_digits=5)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)
    rating = models.CharField(max_length=3, choices=(("1", "1"), ("1.5", "1.5"), ("2", "2"), ("2.5", "2.5"), ("3", "3"), ("3.5", "3.5"), ("4", "4"), ("4.5", "4.5"), ("5", "5")))

    def __str__(self):
        return self.name    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}-{self.game.name}"
