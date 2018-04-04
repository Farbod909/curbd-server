from django.contrib.auth import get_user_model
from django.shortcuts import redirect, reverse
from rest_framework import generics, status, filters
from rest_framework.response import Response

from api.general_permissions import ReadOnly, IsStaff


from .api_permissions import (
    IsAdminOrIsCarOwnerOrIfIsStaffReadOnly, IsStaffOrIsTargetUserOrReadOnly,
    IsAdminOrIsTargetUser)
from .models import Customer, Host, Car
from .serializers import (
    UserDetailSerializer, HighPermissionUserDetailSerializer,
    UserListSerializer, ChangePasswordSerializer,
    CustomerSerializer, HostSerializer, CarSerializer)


class UserList(generics.ListCreateAPIView):
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = (IsStaff,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('email',)
    ordering_fields = ('date_joined', 'first_name', 'last_name', 'email',)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (IsStaffOrIsTargetUserOrReadOnly,)

    def get_serializer_class(self):
        """ The fields we expose in the API depends on the user's superuser status """
        if self.request.user.is_superuser:
            return HighPermissionUserDetailSerializer
        return UserDetailSerializer


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
            # Check old password
            if not instance.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            instance.set_password(serializer.data.get("new_password"))
            instance.save()
            return Response("Success.", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserHost(generics.GenericAPIView):
    queryset = get_user_model().objects.all()

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            return redirect(reverse('host-detail', args=[user.host.pk]))
        except:  # user.host not found
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserCustomer(generics.GenericAPIView):
    queryset = get_user_model().objects.all()

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            return redirect(reverse('customer-detail', args=[user.customer.pk]))
        except:  # user.customer not found
            return Response(status=status.HTTP_404_NOT_FOUND)


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
    permission_classes = (IsAdminOrIsCarOwnerOrIfIsStaffReadOnly,)
    lookup_field = 'license_plate'

