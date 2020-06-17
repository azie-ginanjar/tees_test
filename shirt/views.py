from rest_framework import generics, status

# Create your views here.
from rest_framework.response import Response

from shirt.models import Shirt
from shirt.serializers import ShirtSerializer


class CreateListShirtView(generics.ListCreateAPIView):
    queryset = Shirt.objects.all()
    serializer_class = ShirtSerializer


class ShirtDetailsUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shirt.objects.all()
    serializer_class = ShirtSerializer

    def put(self, request, *args, **kwargs):
        try:
            shirt = self.queryset.get(pk=kwargs["pk"])
            serializer = ShirtSerializer()
            updated_shirt = serializer.update(shirt, request.data)
            return Response(ShirtSerializer(updated_shirt).data)
        except Shirt.DoesNotExist:
            return Response(
                data={
                    "message": "Shirt with id: {} does not exist".format(kwargs["pk"])
                },
                status=status.HTTP_400_BAD_REQUEST
            )
