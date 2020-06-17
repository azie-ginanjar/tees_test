from django.urls import path

from user.views import UserRegisterView, UserListView, UserDetailsView, UserUpdateView

urlpatterns = [
    path("", UserRegisterView.as_view(), name="user-register"),
    path("list", UserListView.as_view(), name="user-list"),
    path("<str:pk>/details", UserDetailsView.as_view(), name="user-details"),
    path("<str:pk>/update", UserUpdateView.as_view(), name="user-update"),
]
