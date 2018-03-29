from django.conf.urls import url, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^auth/', include('rest_framework.urls'), name='rest_framework'),
    url(r'^users/', include('accounts.api_urls')),
]
