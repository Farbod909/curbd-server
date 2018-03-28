from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from accounts import api_views as account_api_views


router = routers.DefaultRouter()
router.register(r'users', account_api_views.UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls'), name='rest_framework'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
