import calendar
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .api_permissions import (
    IsAdminOrIsParkingSpaceOwnerOrReadOnly, IsHostOrReadOnly,
    IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,
    IsAdminOrIsReservationOwnerOrReadOnly, IsCustomerOrReadOnly)
from .api_filters import LocationAndTimeAvailableFilter
from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation
from .serializers import ParkingSpaceSerializer, FixedAvailabilitySerializer, RepeatingAvailabilitySerializer, ReservationSerializer


class ParkingSpaceList(generics.ListCreateAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer
    permission_classes = (IsHostOrReadOnly,)
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
    permission_classes = (IsHostOrReadOnly,)


class FixedAvailabilityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FixedAvailability.objects.all()
    serializer_class = FixedAvailabilitySerializer
    permission_classes = (IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,)


class RepeatingAvailabilityList(generics.ListCreateAPIView):
    queryset = RepeatingAvailability.objects.all()
    serializer_class = RepeatingAvailabilitySerializer
    permission_classes = (IsHostOrReadOnly,)


class RepeatingAvailabilityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RepeatingAvailability.objects.all()
    serializer_class = RepeatingAvailabilitySerializer
    permission_classes = (IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,)


class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsCustomerOrReadOnly,)

    def perform_create(self, serializer):
        parking_space = serializer.validated_data.pop('parking_space')
        start_datetime = serializer.validated_data['start_datetime']
        end_datetime = serializer.validated_data['end_datetime']

        try:
            fixed_availability = FixedAvailability.objects.get(
                Q(parking_space=parking_space),
                Q(start_datetime__lte=start_datetime),
                Q(end_datetime__gte=end_datetime),
            )
            # TODO: make sure this doesn't return more than one object (check for overlap when creating availabilities)
        except ObjectDoesNotExist:
            # if there is no fixed availability move on to
            # check if there is a repeating availability.
            try:
                day_of_week = calendar.day_name[start_datetime.weekday()][:3]
                # POSSIBLE ADDITION: allow start_datetime and end_datetime to be on
                # two different weekdays
                repeating_availability = RepeatingAvailability.objects.get(
                    Q(parking_space=parking_space),
                    Q(start_time__lte=start_datetime.time()),
                    Q(end_time__gte=end_datetime.time()),
                    Q(repeating_days__contains=[day_of_week])
                )
            except ObjectDoesNotExist:
                # neither a fixed availability nor a repeating
                # availability exists.
                raise ValidationError(detail="No availabilities in given time range.")
            else:
                serializer.validated_data['repeating_availability'] = repeating_availability
        else:
            serializer.validated_data['fixed_availability'] = fixed_availability

        return super(ReservationList, self).perform_create(serializer)


class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAdminOrIsReservationOwnerOrReadOnly,)
