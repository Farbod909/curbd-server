from django.conf.urls import url, include
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls'), name='rest_framework'),
    url(r'^users/', include('accounts.api_urls')),
]
