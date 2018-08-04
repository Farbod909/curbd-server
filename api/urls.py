from django.conf.urls import include
from django.urls import path
from rest_framework.authtoken import views as drf_views

from . import views


urlpatterns = [
    path('', views.api_root),
    path('auth/', include('rest_framework.urls'), name='rest_framework'),
    path('auth/token', drf_views.obtain_auth_token, name='auth'),
    path('accounts/', include('accounts.api_urls')),
    path('parking/', include('parking.api_urls')),
    path('payment/', include('payment.api_urls')),
]
