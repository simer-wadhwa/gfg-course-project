from django.db import models
from django.contrib.auth import get_user_model

from todo.choices import StatusChoices

User = get_user_model()

# Create your models here.

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(default=True)
    status = models.CharField(max_length=15,choices =StatusChoices.CHOICE_LIST)
    due_date = models.DateField(blank =True,null =True)
    due_time = models.TimeField(blank =True,null =True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
