from django.urls import path

from . import api_views


urlpatterns = [
    path('ephemeral_keys/', api_views.ephemeral_keys, name='ephemeral_keys'),
    path('charge_reservation/', api_views.charge_reservation, name='charge'),
    path('venmo_payout/', api_views.venmo_payout, name='venmo_payout')
]