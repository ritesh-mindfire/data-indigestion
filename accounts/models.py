from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    pass


class Manufacturer(models.Model):
    name = models.CharField(max_length=64)
    car_model = models.CharField(max_length=64)
    car_year = models.IntegerField()
    country = models.CharField(max_length=64)
    price = models.FloatField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def is_current_year_model(self):
        return datetime.today().year == self.car_year

    
    # def __str__(self):
    #     return self.name
    