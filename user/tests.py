from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.core.files.uploadedfile import SimpleUploadedFile


# tests for views
from user.serializers import UserSerializer

User = get_user_model()


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_user(username, password, first_name, last_name, profile_picture):
        User.objects.create(username=username, password=password, first_name=first_name, last_name=last_name,
                            profile_picture=profile_picture)

    def setUp(self):
        # add test data
        self.create_user(username='test_user', password='test_password', first_name='first', last_name='last',
                         profile_picture=SimpleUploadedFile(name='captcha1.jpg',
                                                            content=open('pictures/test/test_image.jpg', 'rb').read(),
                                                            content_type='image/jpeg'))
        self.create_user(username='test_user1', password='test_password1', first_name='first1', last_name='last1',
                         profile_picture=SimpleUploadedFile(name='captcha2.jpg',
                                                            content=open('pictures/test/test_image.jpg', 'rb').read(),
                                                            content_type='image/jpeg'))


class GetAllUsersTest(BaseViewTest):

    def test_get_all_users(self):
        """
        This test ensures that all songs added in the setUp method
        exist when we make a GET request to the songs/ endpoint
        """
        # hit the API endpoint
        response = self.client.get(
            reverse("user-register-list", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = User.objects.all()
        serialized = UserSerializer(expected, many=True)

        for i in range(len(serialized.data)):
            expected_picture = serialized.data[i].pop('profile_picture')
            picture_from_response = response.data[i].pop('profile_picture')

            self.assertEqual(serialized.data[i], response.data[i])

            assert expected_picture in picture_from_response

        self.assertEqual(response.status_code, status.HTTP_200_OK)
