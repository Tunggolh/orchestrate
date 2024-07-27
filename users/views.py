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
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
