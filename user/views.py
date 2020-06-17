from django.contrib.auth import get_user_model

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from user.serializers import UserSerializer, UserWithoutPasswordSerializer, UserUpdatableFieldSerializer

User = get_user_model()


# Create your views here.
class UserRegisterView(generics.CreateAPIView):
    """
    Register new user
    """
    queryset = User.objects.all().filter(is_active=True)
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class UserListView(generics.ListAPIView):
    """
    Get active user lists
    """
    queryset = User.objects.all().filter(is_active=True)
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserWithoutPasswordSerializer


class UserDetailsView(generics.RetrieveAPIView):
    """
    Retrieve user details by user_id
    """
    queryset = User.objects.all().filter(is_active=True)
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserWithoutPasswordSerializer


class UserUpdateView(generics.UpdateAPIView):
    """
    Takes first_name, last_name, email, and profile picture then return updated user
    to update existing user. This operation just could be accessed by admin user or the users themselves.
    """
    queryset = User.objects.all().filter(is_active=True)
    serializer_class = UserUpdatableFieldSerializer

    def put(self, request, *args, **kwargs):

        if request.user.is_superuser or str(request.user.pk) == kwargs["pk"]:
            try:
                user = self.queryset.get(pk=kwargs["pk"])
                serializer = UserUpdatableFieldSerializer()
                updated_user = serializer.update(user, request.data)
                return Response(UserWithoutPasswordSerializer(updated_user).data)
            except User.DoesNotExist:
                return Response(
                    data={
                        "message": "User with id: {} does not exist".format(kwargs["pk"])
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                data={
                    "message": "Unauthorized"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
