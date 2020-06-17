from django.urls import path

from shirt.views import CreateListShirtView, ShirtDetailsUpdateDeleteView

urlpatterns = [
    path("", CreateListShirtView.as_view(), name="create-list-shirt"),
    path("<str:pk>", ShirtDetailsUpdateDeleteView.as_view(), name="details-update-delete-shirt"),
]
