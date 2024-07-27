"""
URLs for users app
"""

from django.urls import path

from .views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'users'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('me/', RetrieveUpdateUserView.as_view(), name='me'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
