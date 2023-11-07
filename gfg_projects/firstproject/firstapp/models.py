from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()


class Account(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    amount = models.FloatField()
    currency = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.amount}_{self.currency}"
