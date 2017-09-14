from django.http import HttpResponse


def pong(request):
    return HttpResponse("pong")