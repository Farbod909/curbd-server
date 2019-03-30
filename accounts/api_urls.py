from django.urls import path, include

from . import api_views


urlpatterns = [
    path('users/', api_views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', api_views.UserDetail.as_view(), name='user-detail'),
    path('users/self/', api_views.UserSelfDetail.as_view(), name='user-self-detail'),
    path('users/<int:pk>/change_password/', api_views.ChangePassword.as_view(), name='user-change-password'),
    path('users/<int:pk>/reset_password/', api_views.ResetPassword.as_view(), name='user-reset-password'),
    path('users/<int:pk>/customer/', api_views.UserCustomer.as_view(), name='user-customer'),
    path('users/<int:pk>/host/', api_views.UserHost.as_view(), name='user-host'),

    path('forget_password/', include('django_rest_passwordreset.urls', namespace='forget-password')),

    path('customers/', api_views.CustomerList.as_view(), name='customer-list'),
    path('customers/<int:pk>/', api_views.CustomerDetail.as_view(), name='customer-detail'),
    path('customers/self/', api_views.CustomerSelfDetail.as_view(), name='customer-self-detail'),
    path('customers/self/reservations/current/', api_views.CustomerSelfCurrentReservations.as_view(),
         name='customer-self-reservations-current'),
    path('customers/self/reservations/previous/', api_views.CustomerSelfPreviousReservations.as_view(),
         name='customer-self-reservations-previous'),

    path('hosts/', api_views.HostList.as_view(), name='host-list'),
    path('hosts/<int:pk>/', api_views.HostDetail.as_view(), name='host-detail'),
    path('hosts/self/', api_views.HostSelfDetail.as_view(), name='host-self-detail'),
    path('hosts/self/parkingspaces/', api_views.HostSelfParkingSpaces.as_view(), name='host-self-parkingspaces'),
    path('hosts/self/reservations/current/', api_views.HostSelfCurrentReservations.as_view(),
         name='host-self-reservations-current'),
    path('hosts/self/reservations/previous/', api_views.HostSelfPreviousReservations.as_view(),
         name='host-self-reservations-previous'),
    path('hosts/self/verify/', api_views.HostSelfUpdateVerificationInfo.as_view(), name='host-self-verify'),

    path('vehicles/', api_views.VehicleList.as_view(), name='vehicle-list'),
    path('vehicles/<int:pk>/', api_views.VehicleDetail.as_view(), name='vehicle-detail'),
]
