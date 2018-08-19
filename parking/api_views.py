import calendar
import datetime
import pytz
import dateutil.parser

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView


from .api_permissions import (
    IsAdminOrIsParkingSpaceOwnerOrReadOnly, IsHostOrReadOnly,
    IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,
    IsAdminOrIsReservationOwnerOrReadOnly, IsCustomerOrReadOnly,
    IsAuthenticatedOrReadOnly)
from .api_filters import IsActiveFilter, LocationAndTimeAvailableFilter, MinVehicleSizeFilter
from .models import ParkingSpace, ParkingSpaceImage, FixedAvailability, RepeatingAvailability, Reservation
from .serializers import ParkingSpaceSerializer, FixedAvailabilitySerializer, RepeatingAvailabilitySerializer, ReservationSerializer
from accounts.models import Host, Address


class ParkingSpaceList(generics.ListCreateAPIView):
    queryset = ParkingSpace.objects.all().order_by('-created_at')
    serializer_class = ParkingSpaceSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IsActiveFilter, MinVehicleSizeFilter, LocationAndTimeAvailableFilter)
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):

        # create address and attach to parking space
        try:
            address1 = self.request.data['address1']
            address2 = self.request.data.get('address2', None)
            city = self.request.data['city']
            state = self.request.data['state']
            code = self.request.data['code']
        except MultiValueDictKeyError:
            raise ValidationError("Incomplete address fields")

        try:
            address = Address.objects.get(address1=address1, address2=address2, city=city, state=state, code=code)
        except Address.DoesNotExist:
            address = Address.objects.create(address1=address1, address2=address2, city=city, state=state, code=code)

        serializer.validated_data['address'] = address

        # set parking space host
        try:
            serializer.validated_data['host'] = self.request.user.host
        except Host.DoesNotExist:
            host = Host.objects.create(user=self.request.user)
            serializer.validated_data['host'] = host

        # create parking space images
        parking_space = serializer.save()

        for image in self.request.data.getlist('images'):
            ParkingSpaceImage.objects.create(image=image, parking_space=parking_space)

        return parking_space


class ParkingSpaceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer
    permission_classes = (IsAdminOrIsParkingSpaceOwnerOrReadOnly,)


class FixedAvailabilityList(generics.ListCreateAPIView):
    queryset = FixedAvailability.objects.all().order_by('-start_datetime')
    serializer_class = FixedAvailabilitySerializer
    permission_classes = (IsHostOrReadOnly,)


class FixedAvailabilityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FixedAvailability.objects.all()
    serializer_class = FixedAvailabilitySerializer
    permission_classes = (IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,)


class RepeatingAvailabilityList(generics.ListCreateAPIView):
    queryset = RepeatingAvailability.objects.all().order_by('-created_at')
    serializer_class = RepeatingAvailabilitySerializer
    permission_classes = (IsHostOrReadOnly,)


class RepeatingAvailabilityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RepeatingAvailability.objects.all()
    serializer_class = RepeatingAvailabilitySerializer
    permission_classes = (IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly,)


class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.all().order_by('-created_at')
    serializer_class = ReservationSerializer
    permission_classes = (IsCustomerOrReadOnly,)

    def perform_create(self, serializer):
        parking_space = serializer.validated_data.pop('parking_space_id')
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
                    Q(parking_space=parking_space) &
                    (Q(all_day=True) | (Q(start_time__lte=start_datetime.time()) & Q(end_time__gte=end_datetime.time()))) &
                    Q(repeating_days__contains=[day_of_week]))

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


class ParkingSpaceAvailability(generics.RetrieveAPIView):
    queryset = ParkingSpace.objects.all()

    def get_serializer_class(self):
        parking_space = super(ParkingSpaceAvailability, self).get_object()
        start_datetime_iso = self.request.query_params['start']
        end_datetime_iso = self.request.query_params['end']

        # TODO: convert this to local time zone similar to parking space search filter
        start_datetime = dateutil.parser.parse(start_datetime_iso)
        end_datetime = dateutil.parser.parse(end_datetime_iso)

        day_of_week = calendar.day_name[start_datetime.weekday()][:3]
        try:
            RepeatingAvailability.objects.get(
                Q(parking_space=parking_space) &
                (Q(all_day=True) | (Q(start_time__lte=start_datetime.time()) & Q(end_time__gte=end_datetime.time()))) &
                Q(repeating_days__contains=[day_of_week])
            )
        except ObjectDoesNotExist:
            try:
                FixedAvailability.objects.get(
                    Q(parking_space=parking_space),
                    Q(start_datetime__lte=start_datetime),
                    Q(end_datetime__gte=end_datetime),
                )
            except ObjectDoesNotExist:
                raise ValidationError(detail="No availabilities in given time range.")
            else:
                return FixedAvailabilitySerializer
        else:
            return RepeatingAvailabilitySerializer

    def get_object(self):
        parking_space = super(ParkingSpaceAvailability, self).get_object()
        start_datetime_iso = self.request.query_params['start']
        end_datetime_iso = self.request.query_params['end']

        start_datetime = dateutil.parser.parse(start_datetime_iso)
        end_datetime = dateutil.parser.parse(end_datetime_iso)

        day_of_week = calendar.day_name[start_datetime.weekday()][:3]
        try:
            return RepeatingAvailability.objects.get(
                Q(parking_space=parking_space) &
                (Q(all_day=True) | (Q(start_time__lte=start_datetime.time()) & Q(end_time__gte=end_datetime.time()))) &
                Q(repeating_days__contains=[day_of_week])
            )
        except ObjectDoesNotExist:
            try:
                return FixedAvailability.objects.get(
                    Q(parking_space=parking_space),
                    Q(start_datetime__lte=start_datetime),
                    Q(end_datetime__gte=end_datetime),
                )
            except ObjectDoesNotExist:
                raise ValidationError(detail="No availabilities in given time range.")


class ParkingSpaceRepeatingAvailabilities(generics.ListAPIView):
    serializer_class = RepeatingAvailabilitySerializer
    permission_classes = (IsHostOrReadOnly,)

    def get_queryset(self):
        return RepeatingAvailability.objects.filter(parking_space=self.kwargs['pk']).order_by('-created_at')


class ParkingSpaceFixedAvailabilities(generics.ListAPIView):
    serializer_class = FixedAvailabilitySerializer
    permission_classes = (IsHostOrReadOnly,)

    def get_queryset(self):
        return FixedAvailability.objects.filter(parking_space=self.kwargs['pk']).order_by('-start_datetime')


class ParkingSpaceFixedAvailabilitiesFuture(generics.ListAPIView):
    serializer_class = FixedAvailabilitySerializer
    permission_classes = (IsHostOrReadOnly,)

    def get_queryset(self):
        return FixedAvailability.objects.filter(
            parking_space=self.kwargs['pk'], end_datetime__gte=datetime.datetime.now(pytz.utc)).order_by('-start_datetime')


class ParkingSpaceCurrentReservations(generics.ListAPIView):
    serializer_class = ReservationSerializer
    permission_classes = (IsHostOrReadOnly,)

    def get_queryset(self):
        return ParkingSpace.objects.get(pk=self.kwargs['pk']).reservations().filter(
            end_datetime__gte=datetime.datetime.now(pytz.utc)).order_by('-start_datetime')


class ParkingSpacePreviousReservations(generics.ListAPIView):
    serializer_class = ReservationSerializer
    permission_classes = (IsHostOrReadOnly,)

    def get_queryset(self):
        return ParkingSpace.objects.get(pk=self.kwargs['pk']).reservations().filter(
            end_datetime__lt=datetime.datetime.now(pytz.utc)).order_by('-start_datetime')


class ReservationReport(APIView):

    def get_object(self, pk):
        try:
            return Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        reservation = self.get_object(pk)
        return Response("Success", status=status.HTTP_200_OK)


class ReservationCancel(APIView):

    def get_object(self, pk):
        try:
            return Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        reservation = self.get_object(pk)

        if reservation.start_datetime > datetime.datetime.now(pytz.utc) or \
                reservation.vehicle.customer != request.user.customer:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            reservation.cancelled = True
            reservation.save()
            # TODO: send email
            return Response("Success", status=status.HTTP_200_OK)

