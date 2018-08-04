from django.urls import path

from . import api_views


urlpatterns = [
    path('ephemeral_keys/', api_views.ephemeral_keys, name='ephemeral_keys'),
    path('charge/', api_views.charge, name='charge'),
]