from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response

from api.permissions import ReadOnly


from .api_permissions import IsStaff, IsAdminOrIsCarOwnerOrIsStaffReadOnly, IsStaffOrIsUserOrReadOnly
from .models import Customer, Host, Car
from .serializers import (
    UserSerializer, HighPermissionUserSerializer, UserListSerializer,
    CustomerSerializer, HostSerializer, CarSerializer)


class UserList(generics.ListAPIView):
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = (IsStaff,)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (IsStaffOrIsUserOrReadOnly,)

    def get_serializer_class(self):
        """ The fields we expose in the API depends on the user's superuser status """
        if self.request.user.is_superuser:
            return HighPermissionUserSerializer
        return UserSerializer


class UserIsHost(generics.GenericAPIView):
    queryset = get_user_model().objects.all()

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        return Response(user.is_host())


class CustomerList(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsStaff,)


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (ReadOnly,)


class HostList(generics.ListCreateAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = (IsStaff,)


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = (ReadOnly,)


class CarList(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsStaff,)


class CarDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsAdminOrIsCarOwnerOrIsStaffReadOnly,)
    lookup_field = 'license_plate'

