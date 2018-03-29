from django.contrib.auth import get_user_model
from rest_framework import generics

from .api_permissions import IsAdminOrIsOwnerOrReadOnly
from .serializers import UserSerializer


class UserList(generics.ListAPIView):
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrIsOwnerOrReadOnly,)
