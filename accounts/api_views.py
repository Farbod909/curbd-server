from django.contrib.auth import get_user_model
from rest_framework import generics

from .api_permissions import IsAdminOrIsUserOrReadOnly
from .serializers import  UserSerializer, HighPermissionUserSerializer, UserListSerializer


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

