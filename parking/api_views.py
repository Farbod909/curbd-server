import calendar
import datetime
import pytz
import dateutil.parser

from decouple import config
from timezonefinder import TimezoneFinder

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
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
from .helpers import lat_degrees_from_miles, long_degrees_from_miles_at_lat, get_weekday_span_between
from .models import ParkingSpace, ParkingSpaceImage, FixedAvailability, RepeatingAvailability, Reservation
from .serializers import (
    ParkingSpaceSerializer, FixedAvailabilitySerializer,
    RepeatingAvailabilitySerializer, ReservationSerializer, ParkingSpaceMinimalSerializer)
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


class ParkingSpaceSearch(APIView):
    queryset = ParkingSpace.objects.all()

    def get(self, request):
        bottom_left_lat = request.query_params.get('bl_lat', None)
        bottom_left_long = request.query_params.get('bl_long', None)
        top_right_lat = request.query_params.get('tr_lat', None)
        top_right_long = request.query_params.get('tr_long', None)
        start_datetime_iso = request.query_params.get('start', None)
        end_datetime_iso = request.query_params.get('end', None)
        min_vehicle_size = request.query_params.get('size', None)

        """PRE-PROCESS INPUTS"""
        # first we need to reduce the box size if it's too large
        max_search_radius = 6  # in miles

        bottom_left_lat = float(bottom_left_lat)
        bottom_left_long = float(bottom_left_long)
        top_right_lat = float(top_right_lat)
        top_right_long = float(top_right_long)

        center_lat = (bottom_left_lat + top_right_lat) / 2.0
        center_long = (bottom_left_long + top_right_long) / 2.0

        max_lat_degrees_distance = lat_degrees_from_miles(max_search_radius)
        if max_lat_degrees_distance < abs(top_right_lat - center_lat):
            top_right_lat = center_lat + max_lat_degrees_distance
            bottom_left_lat = center_lat - max_lat_degrees_distance

        max_long_degrees_distance = long_degrees_from_miles_at_lat(max_search_radius, center_lat)
        if max_long_degrees_distance < abs(top_right_long - center_long):
            top_right_long = center_long + max_long_degrees_distance
            bottom_left_long = center_long - max_long_degrees_distance

        # adjust input datetimes for map timezone
        start_datetime = dateutil.parser.parse(start_datetime_iso)
        end_datetime = dateutil.parser.parse(end_datetime_iso)

        if start_datetime.tzinfo is None or end_datetime.tzinfo is None:
            raise ValidationError("Timezone must be provided")

        if start_datetime >= end_datetime:
            raise ValidationError("end must be a later date than start")

        tf = TimezoneFinder()

        median_lat = (float(bottom_left_lat) + float(top_right_lat)) / 2
        median_lng = (float(bottom_left_long) + float(top_right_long)) / 2

        timezone_name = tf.timezone_at(lat=median_lat, lng=median_lng)

        if timezone_name is None:
            timezone_name = tf.closest_timezone_at(lng=median_lat, lat=median_lng)

        if timezone_name is not None:
            try:
                tz = pytz.timezone(timezone_name)
            except pytz.exceptions.UnknownTimeZoneError:
                # fall back to the timezone that came with the request
                pass
            else:
                naive_start_datetime = start_datetime.replace(tzinfo=None)
                naive_end_datetime = end_datetime.replace(tzinfo=None)

                start_datetime = tz.localize(naive_start_datetime)
                end_datetime = tz.localize(naive_end_datetime)

        """QUERY AVAILABLE PARKING SPACES"""
        # determine the day of the week the user is searching for
        start_day_of_week = calendar.day_name[start_datetime.weekday()][:3]
        end_day_of_week = calendar.day_name[end_datetime.weekday()][:3]

        if start_day_of_week == end_day_of_week:
            repeating_availabilities = RepeatingAvailability.objects.select_related('parking_space').filter(
                (
                    Q(parking_space__is_active=True) &
                    Q(parking_space__longitude__gte=bottom_left_long) &
                    Q(parking_space__longitude__lte=top_right_long) &
                    Q(parking_space__latitude__gte=bottom_left_lat) &
                    Q(parking_space__latitude__lte=top_right_lat)
                ) &
                Q(repeating_days__contains=[start_day_of_week]) &
                (
                    Q(all_day=True) |
                    (Q(start_time__lte=start_datetime.time()) & Q(end_time__gte=end_datetime.time()))
                )
            )
        else:
            # reserving a spot over the span of multiple days
            weekdays = get_weekday_span_between(start_day_of_week, end_day_of_week)
            repeating_availabilities = RepeatingAvailability.objects.select_related('parking_space').filter(
                (
                    Q(parking_space__is_active=True) &
                    Q(parking_space__longitude__gte=bottom_left_long) &
                    Q(parking_space__longitude__lte=top_right_long) &
                    Q(parking_space__latitude__gte=bottom_left_lat) &
                    Q(parking_space__latitude__lte=top_right_lat)
                ) &
                (
                    Q(repeating_days__contains=weekdays) &
                    Q(all_day=True)
                )
            )

        fixed_availabilities = FixedAvailability.objects.select_related('parking_space').filter(
            (
                Q(parking_space__is_active=True) &
                Q(parking_space__longitude__gte=bottom_left_long) &
                Q(parking_space__longitude__lte=top_right_long) &
                Q(parking_space__latitude__gte=bottom_left_lat) &
                Q(parking_space__latitude__lte=top_right_lat)
            ) &
            (
                Q(start_datetime__lte=start_datetime) &
                Q(end_datetime__gte=end_datetime)
            )
        )

        if min_vehicle_size is not None:
            repeating_availabilities = repeating_availabilities.filter(parking_space__size__gte=min_vehicle_size)
            fixed_availabilities = fixed_availabilities.filter(parking_space__size__gte=min_vehicle_size)

        parking_space_ids = set()
        available_spaces_map = dict()
        parking_spaces_map = dict()

        for ra in repeating_availabilities:
            parking_space_ids.add(ra.parking_space_id)
            available_spaces_map[ra.parking_space_id] = ra.parking_space.available_spaces
            parking_spaces_map[ra.parking_space_id] = (ra.parking_space, ra.pricing)

        for fa in fixed_availabilities:
            parking_space_ids.add(fa.parking_space_id)
            available_spaces_map[fa.parking_space_id] = fa.parking_space.available_spaces
            # If a repeating and fixed availability have overlap, the next line
            # will overwrite the pricing from the repeating availability. This is
            # intended behavior. Fixed availability pricing has priority.
            parking_spaces_map[fa.parking_space_id] = (fa.parking_space, fa.pricing)

        reservations = Reservation.objects.filter(
            parking_space__in=parking_space_ids,
            start_datetime__lte=end_datetime,
            end_datetime__gte=start_datetime,
            cancelled=False)

        for reservation in reservations:
            available_spaces_map[reservation.parking_space_id] -= 1

        for parking_space_id, available_spaces in available_spaces_map.items():
            if available_spaces == 0:
                del parking_spaces_map[parking_space_id]

        parking_spaces = [
            {
                "parking_space": ParkingSpaceMinimalSerializer(parking_space).data,
                "pricing": pricing
            }
            for parking_space_id, (parking_space, pricing) in parking_spaces_map.items()]

        return Response({
            "count": len(parking_spaces),
            "results": parking_spaces,
        })


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
    queryset = Reservation.objects.all()

    def get_object(self, pk):
        try:
            return Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        reservation = self.get_object(pk)
        title = request.data.get("title")
        comments = request.data.get("comments", "None")
        reporter = request.user
        reporter_type = request.data.get("reporter_type")

        send_mail(
            '[REPORT]',
            "reservation id: %s,\n title: %s,\n comments: %s,\n reporter full name: %s,\n reporter id: %s,\n reporter type: %s" %
            (reservation.id, title, comments, reporter.get_full_name(), reporter.id, reporter_type),
            'no-reply@curbdparking.com', [config('REPORT_RECIPIENT')])

        return Response("Success", status=status.HTTP_200_OK)


class ReservationCancel(APIView):
    queryset = Reservation.objects.all()

    def get_object(self, pk):
        try:
            return Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        reservation = self.get_object(pk)

        if reservation.start_datetime < datetime.datetime.now(pytz.utc) or \
                reservation.vehicle.customer != request.user.customer:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            reservation.cancelled = True
            reservation.save()

            send_mail(
                '[CANCELLATION]',
                "reservation id: %s,\n reservation cost: %s,\n reservation host income: %s,\n reserver id: %s,\n reserver full name: %s" %
                (reservation.id, reservation.cost, reservation.host_income,
                 reservation.vehicle.customer.user.id, reservation.vehicle.customer.user.get_full_name()),
                'no-reply@curbdparking.com', [config('CANCEL_RECIPIENT')])

            return Response("Success", status=status.HTTP_200_OK)

