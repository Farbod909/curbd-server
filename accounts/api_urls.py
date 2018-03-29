from django.conf.urls import url

from . import api_views


urlpatterns = [
    url(r'^$', api_views.UserList.as_view(), name='user-list'),
    url(r'^(?P<pk>[0-9]+)/$', api_views.UserDetail.as_view(), name='user-detail'),
]