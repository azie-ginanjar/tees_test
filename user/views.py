from django.contrib.auth import get_user_model
from django.shortcuts import render


# Create your views here.
from rest_framework import generics

from user.serializers import UserSerializer

User = get_user_model()


class User(generics.ListCreateAPIView):
    queryset = User.objects.all().filter(is_active=True)
    # permission_classes = (AdminRequired, )
    serializer_class = UserSerializer
