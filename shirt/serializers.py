from rest_framework import serializers

from shirt.models import Shirt


class ShirtSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shirt
        fields = ("id", "name", "email", "size")
