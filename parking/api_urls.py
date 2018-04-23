from django.urls import path

from . import api_views


urlpatterns = [
    path('spaces/', api_views.ParkingSpaceList.as_view(), name='parkingspace-list'),
    path('spaces/<int:pk>/', api_views.ParkingSpaceDetail.as_view(), name='parkingspace-detail'),
    path('spaces/<int:pk>/availability', api_views.ParkingSpaceAvailability.as_view(), name='parkingspace-availability'),
    path('fixedavailabilities/', api_views.FixedAvailabilityList.as_view(), name='fixedavailability-list'),
    path('fixedavailabilities/<int:pk>/', api_views.FixedAvailabilityDetail.as_view(), name='fixedavailability-detail'),
    path('repeatingavailablities/', api_views.RepeatingAvailabilityList.as_view(), name='repeatingavailability-list'),
    path('repeatingavailablities/<int:pk>/', api_views.RepeatingAvailabilityDetail.as_view(), name='repeatingavailability-detail'),
    path('reservations/', api_views.ReservationList.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/', api_views.ReservationDetail.as_view(), name='reservation-detail'),
]