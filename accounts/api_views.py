import dateutil.parser
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework import generics, status, filters, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.views import APIView

import datetime
import pytz

from api.general_permissions import ReadOnly, IsStaff
from .api_permissions import (
    IsAdminOrIsVehicleOwnerOrIfIsStaffReadOnly, IsStaffOrIsTargetUserOrReadOnly,
    IsAdminOrIsTargetUser, IsStaffOrWriteOnly, CustomersCanCreateStaffCanRead,
    StaffCanReadAndHostsCanWrite, IsHost)
from .models import Customer, Host, Vehicle, Address
from .pagination import PreviousReservationsCursorPagination
from .serializers import (
    UserListSerializer, UserDetailSerializer,
    ChangePasswordSerializer,
    CustomerSerializer, HostSerializer, VehicleSerializer)


class UserList(generics.ListCreateAPIView):
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = (IsStaffOrWriteOnly,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('email',)
    ordering_fields = ('date_joined', 'first_name', 'last_name', 'email',)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (IsStaffOrIsTargetUserOrReadOnly,)


class UserSelfDetail(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ChangePassword(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    queryset = get_user_model().objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAdminOrIsTargetUser,)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not instance.check_password(serializer.data.get("old_password")):
                raise ValidationError(detail={"old_password": "Wrong password"})  # 400 bad request

            instance.set_password(serializer.data.get("new_password"))
            instance.save()
            return Response(status=status.HTTP_200_OK)

        raise ParseError(detail=serializer.errors)  # 400 bad request


class UserHost(generics.RetrieveAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = HostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        user = super(UserHost, self).get_object()
        try:
            return user.host
        except Host.DoesNotExist:
            raise Http404


class UserCustomer(generics.RetrieveAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        user = super(UserCustomer, self).get_object()
        try:
            return user.customer
        except Customer.DoesNotExist:
            raise Http404


class CustomerList(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsStaff,)


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (ReadOnly,)


class CustomerSelfDetail(generics.RetrieveAPIView):
    serializer_class = CustomerSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        try:
            return self.request.user.customer
        except Customer.DoesNotExist:
            raise Http404


class CustomerSelfCurrentReservations(generics.ListAPIView):
    from parking.serializers import ReservationSerializer
    serializer_class = ReservationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.customer.reservations().filter(
            end_datetime__gte=datetime.datetime.now(tz=pytz.timezone('America/Los_Angeles'))).order_by('start_datetime')


class CustomerSelfPreviousReservations(generics.ListAPIView):
    from parking.serializers import ReservationSerializer
    serializer_class = ReservationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PreviousReservationsCursorPagination

    def get_queryset(self):
        return self.request.user.customer.reservations().filter(
            end_datetime__lt=datetime.datetime.now(tz=pytz.timezone('America/Los_Angeles'))).order_by('-start_datetime')


class HostList(generics.ListAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = (IsStaff,)
    # POSSIBLE ADDITION: change to ListCreateAPIView and override perform_create
    # to automatically set host


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = (ReadOnly,)


class HostSelfDetail(generics.RetrieveAPIView):
    serializer_class = HostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        try:
            return self.request.user.host
        except Host.DoesNotExist:
            raise Http404


class HostSelfParkingSpaces(generics.ListAPIView):
    from parking.serializers import ParkingSpaceSerializer
    serializer_class = ParkingSpaceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        try:
            return self.request.user.host.parkingspace_set.all()
        except Host.DoesNotExist:
            raise Http404


class HostSelfCurrentReservations(generics.ListAPIView):
    from parking.serializers import ReservationSerializer
    serializer_class = ReservationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        try:
            return self.request.user.host.reservations().filter(
                end_datetime__gte=datetime.datetime.now(tz=pytz.timezone('America/Los_Angeles'))).order_by('start_datetime')
        except Host.DoesNotExist:
            raise Http404


class HostSelfPreviousReservations(generics.ListAPIView):
    from parking.serializers import ReservationSerializer
    serializer_class = ReservationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PreviousReservationsCursorPagination

    def get_queryset(self):
        try:
            return self.request.user.host.reservations().filter(
                end_datetime__lt=datetime.datetime.now(tz=pytz.timezone('America/Los_Angeles'))).order_by('-start_datetime')
        except Host.DoesNotExist:
            raise Http404


class HostSelfUpdateVerificationInfo(APIView):
    queryset = Host.objects.all()
    permission_classes = (IsHost,)

    def put(self, request):

        host = request.user.host

        try:
            address1 = request.data['address1']
            address2 = request.data.get('address2', None)
            city = request.data['city']
            state = request.data['state']
            code = request.data['code']
            date_of_birth = request.data['date_of_birth']
        except MultiValueDictKeyError:
            raise ValidationError("Incomplete fields")

        try:
            address = Address.objects.get(address1=address1, address2=address2, city=city, state=state, code=code)
        except Address.DoesNotExist:
            address = Address.objects.create(address1=address1, address2=address2, city=city, state=state, code=code)

        host.address = address
        host.date_of_birth = dateutil.parser.parse(date_of_birth)
        host.save()

        return Response("Success", status=200)


class VehicleList(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = (CustomersCanCreateStaffCanRead,)

    def perform_create(self, serializer):
        serializer.validated_data['customer'] = self.request.user.customer
        return super(VehicleList, self).perform_create(serializer)


class VehicleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = (IsAdminOrIsVehicleOwnerOrIfIsStaffReadOnly,)

