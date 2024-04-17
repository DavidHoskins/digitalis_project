from django.db import models

# Create your models here.
class Lift(models.Model):
    current_floor = models.IntegerField()
    serviced_floors = models.CharField(max_length=100)
    destination_floors = models.CharField(max_length=100)