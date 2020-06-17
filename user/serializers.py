from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name", "email", "profile_picture")

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        user.password = None
        return user


class UserWithoutPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "profile_picture")


class UserUpdatableFieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "profile_picture")
