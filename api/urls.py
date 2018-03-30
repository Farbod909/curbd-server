from django.conf.urls import include
from django.urls import path
from . import views


urlpatterns = [
    path('', views.api_root),
    path('auth/', include('rest_framework.urls'), name='rest_framework'),
    path('accounts/', include('accounts.api_urls')),
    path('parking/', include('parking.api_urls')),
]
