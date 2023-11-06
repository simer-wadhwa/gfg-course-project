from django.shortcuts import render
from django.http import HttpResponse
from .models import Account

def startpage(request):
    a = Account.objects.create(
        name = "Simer",
        cash = 100000

    )
    a_fetch = Account.objects.all()
    print(a_fetch)
    return HttpResponse(" Start the page")

# Create your views here.
