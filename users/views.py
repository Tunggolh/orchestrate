"""
This file contains the views for the users app.
"""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.serializers import UserSerializer
from users.models import User


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'
