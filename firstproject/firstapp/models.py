from django.db import models

# Create your models here.

class Account(models.Model):
    name = models.CharField(max_length=10)
    cash = models.FloatField()
