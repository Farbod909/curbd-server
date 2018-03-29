from django.urls import path

from . import api_views


urlpatterns = [
    path('users/', api_views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', api_views.UserDetail.as_view(), name='user-detail'),
    # path('users/<int:pk>/is_host', api_views.UserIsHost.as_view(), name='user-is_host'),
    path('customers/', api_views.CustomerList.as_view(), name='customer-list'),
    # path('customers/<int:pk>', api_views.UserDetail.as_view(), name='customer-detail'),
    path('hosts/', api_views.HostList.as_view(), name='host-list'),
    # path('hosts/<int:pk>', api_views.UserDetail.as_view(), name='host-detail'),
    path('cars/', api_views.CarList.as_view(), name='car-list'),
    path('cars/<license_plate>', api_views.CarDetail.as_view(), name='car-detail'),
]