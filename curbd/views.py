from django.http import HttpResponse

import os

from .settings import BASE_DIR


def apple_app_site_association_view(request):
    path = os.path.join(BASE_DIR, 'static', 'apple-app-site-association')
    with open(path, 'r') as file:
        data = file.read()
    response = HttpResponse(content=data)
    response['Content-Type'] = 'application/json'
    return response
