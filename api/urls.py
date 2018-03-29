from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()

urlpatterns = [
    path('', views.api_root),
    path('auth/', include('rest_framework.urls'), name='rest_framework'),
    path('users/', include('accounts.api_urls')),
]
