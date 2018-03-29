from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


from .api_permissions import IsAdminOrIsUserOrReadOnly
from .models import Customer, Host
from .serializers import (
    UserSerializer, HighPermissionUserSerializer, UserListSerializer,
    CustomerSerializer, HostSerializer)


class UserList(generics.ListAPIView):
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (IsAdminOrIsUserOrReadOnly,)

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


class HostList(generics.ListCreateAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

