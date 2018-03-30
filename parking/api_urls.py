from django.urls import path

from . import api_views


urlpatterns = [
    path('spaces/', api_views.ParkingSpaceList.as_view(), name='parkingspace-list'),
    path('spaces/<int:pk>', api_views.ParkingSpaceDetail.as_view(), name='parkingspace-detail'),
]