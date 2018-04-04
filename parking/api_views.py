from rest_framework import generics
from rest_framework import permissions

from .api_permissions import (
    IsAdminOrIsParkingSpaceOwnerOrReadOnly, HostsCanCreateAndStaffCanRead,
    IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,
    IsAdminOrIsReservationOwnerOrReadOnly,)
from .api_filters import LocationAndTimeAvailableFilter
from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation
from .serializers import ParkingSpaceSerializer, FixedAvailabilitySerializer, RepeatingAvailabilitySerializer, ReservationSerializer


class ParkingSpaceList(generics.ListCreateAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer
    permission_classes = (HostsCanCreateAndStaffCanRead,)
    filter_backends = (LocationAndTimeAvailableFilter,)

    def perform_create(self, serializer):
        serializer.validated_data['host'] = self.request.user.host
        return super(ParkingSpaceList, self).perform_create(serializer)


class ParkingSpaceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer
    permission_classes = (IsAdminOrIsParkingSpaceOwnerOrReadOnly,)


class FixedAvailabilityList(generics.ListCreateAPIView):
    queryset = FixedAvailability.objects.all()
    serializer_class = FixedAvailabilitySerializer
    permission_classes = (HostsCanCreateAndStaffCanRead,)


class FixedAvailabilityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FixedAvailability.objects.all()
    serializer_class = FixedAvailabilitySerializer
    permission_classes = (IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,)


class RepeatingAvailabilityList(generics.ListCreateAPIView):
    queryset = RepeatingAvailability.objects.all()
    serializer_class = RepeatingAvailabilitySerializer
    permission_classes = (HostsCanCreateAndStaffCanRead,)


class RepeatingAvailabilityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RepeatingAvailability.objects.all()
    serializer_class = RepeatingAvailabilitySerializer
    permission_classes = (IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,)


class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAdminOrIsReservationOwnerOrReadOnly,)
