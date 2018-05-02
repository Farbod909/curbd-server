from django.urls import path

from . import api_views


urlpatterns = [
    path('users/', api_views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', api_views.UserDetail.as_view(), name='user-detail'),
    path('users/self/', api_views.UserSelfDetail.as_view(), name='user-self-detail'),
    path('users/<int:pk>/change_password/', api_views.ChangePassword.as_view(), name='user-change-password'),
    path('users/<int:pk>/customer/', api_views.UserCustomer.as_view(), name='user-customer'),
    path('users/<int:pk>/host/', api_views.UserHost.as_view(), name='user-host'),

    path('customers/', api_views.CustomerList.as_view(), name='customer-list'),
    path('customers/<int:pk>/', api_views.CustomerDetail.as_view(), name='customer-detail'),
    path('customers/self/', api_views.CustomerSelfDetail.as_view(), name='customer-self-detail'),
    path('customers/self/reservations/current/', api_views.CustomerSelfReservationsCurrent.as_view(),
         name='customer-self-reservations-current'),
    path('customers/self/reservations/previous/', api_views.CustomerSelfReservationsPrevious.as_view(),
         name='customer-self-reservations-previous'),

    path('hosts/', api_views.HostList.as_view(), name='host-list'),
    path('hosts/<int:pk>/', api_views.HostDetail.as_view(), name='host-detail'),
    path('hosts/self/', api_views.HostSelfDetail.as_view(), name='host-self-detail'),

    path('cars/', api_views.CarList.as_view(), name='car-list'),
    path('cars/<int:pk>/', api_views.CarDetail.as_view(), name='car-detail'),
]
