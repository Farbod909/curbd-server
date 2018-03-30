from rest_framework import generics

from api.permissions import IsStaff
from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation
from .serializers import ParkingSpaceSerializer, FixedAvailabilitySerializer, RepeatingAvailabilitySerializer, ReservationSerializer


class ParkingSpaceList(generics.ListCreateAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer
    permission_classes = (IsStaff,)


class ParkingSpaceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer


class FixedAvailabilityList(generics.ListCreateAPIView):
    queryset = FixedAvailability.objects.all()
    serializer_class = FixedAvailabilitySerializer


class FixedAvailabilityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FixedAvailability.objects.all()
    serializer_class = FixedAvailabilitySerializer


class RepeatingAvailabilityList(generics.ListCreateAPIView):
    queryset = RepeatingAvailability.objects.all()
    serializer_class = RepeatingAvailabilitySerializer


class RepeatingAvailabilityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RepeatingAvailability.objects.all()
    serializer_class = RepeatingAvailabilitySerializer


class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
