from django.urls import path

from . import api_views


urlpatterns = [
    path('spaces/', api_views.ParkingSpaceList.as_view(), name='parkingspace-list'),
    path('spaces/<int:pk>/', api_views.ParkingSpaceDetail.as_view(), name='parkingspace-detail'),
    path('spaces/<int:pk>/availability/', api_views.ParkingSpaceAvailability.as_view(), name='parkingspace-availability'),
    path('spaces/<int:pk>/repeatingavailabilities/', api_views.ParkingSpaceRepeatingAvailabilities.as_view(),
         name='parkingspace-repeatingavailabilities'),
    path('spaces/<int:pk>/fixedavailabilities/', api_views.ParkingSpaceFixedAvailabilities.as_view(),
         name='parkingspace-fixedavailabilities'),
    path('spaces/<int:pk>/fixedavailabilities/future/', api_views.ParkingSpaceFixedAvailabilitiesFuture.as_view(),
         name='parkingspace-fixedavailabilities-future'),
    path('spaces/<int:pk>/reservations/current/', api_views.ParkingSpaceCurrentReservations.as_view(),
         name='parkingspace-reservations-current'),
    path('spaces/<int:pk>/reservations/previous/', api_views.ParkingSpacePreviousReservations.as_view(),
         name='parkingspace-reservations-previous'),

    path('fixedavailabilities/', api_views.FixedAvailabilityList.as_view(), name='fixedavailability-list'),
    path('fixedavailabilities/<int:pk>/', api_views.FixedAvailabilityDetail.as_view(), name='fixedavailability-detail'),

    path('repeatingavailabilities/', api_views.RepeatingAvailabilityList.as_view(), name='repeatingavailability-list'),
    path('repeatingavailabilities/<int:pk>/', api_views.RepeatingAvailabilityDetail.as_view(), name='repeatingavailability-detail'),

    path('reservations/', api_views.ReservationList.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/', api_views.ReservationDetail.as_view(), name='reservation-detail'),
    path('reservations/<int:pk>/report/', api_views.ReservationReport.as_view(), name='reservation-report'),
    path('reservations/<int:pk>/cancel/', api_views.ReservationCancel.as_view(), name='reservation-cancel'),
    # path('reservations/<int:pk>/extend/', api_views.ReservationExtend.as_view(), name='reservation-extend'),

]