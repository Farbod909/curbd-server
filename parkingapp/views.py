from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return HttpResponse("hey there! im broken inside too :/")
