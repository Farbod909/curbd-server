from django.urls import path

from . import api_views


urlpatterns = [
    path('', api_views.UserList.as_view(), name='user-list'),
    path('<int:pk>/', api_views.UserDetail.as_view(), name='user-detail'),
]