import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.core.files.uploadedfile import SimpleUploadedFile

from shirt.models import Shirt
from shirt.serializers import ShirtSerializer
from user.serializers import UserSerializer, UserWithoutPasswordSerializer

User = get_user_model()


# tests for models
class ShirtModelTest(APITestCase):
    def setUp(self):
        self.shirt = Shirt.objects.create(name="name", email="name@testmail.com", size=20)

    def test_shirt(self):
        """"
        This test ensures that the shirt created in the setup
        exists
        """
        shirts = Shirt.objects.all()

        self.assertEqual(self.shirt.name, shirts[0].name)
        self.assertEqual(self.shirt.email, shirts[0].email)
        self.assertEqual(self.shirt.size, shirts[0].size)


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def add_shirt(name, email, size):
        Shirt.objects.create(name=name, email=email, size=size)

    def login_client(self, username, password):
        # get a token
        response = self.client.post(
            reverse("token_obtain_pair"),
            data=json.dumps(
                {
                    'username': username,
                    'password': password
                }
            ),
            content_type='application/json'
        )
        self.token = response.data['access']

        # set the token in the header
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.token
        )
        self.client.login(username=username, password=password)
        return self.token

    def get_shirt_details(self, pk=0):
        return self.client.get(
            reverse(
                "details-update-delete-shirt",
                kwargs={
                    "version": "v1",
                    "pk": pk
                }
            )
        )

    def update_shirt(self, **kwargs):
        return self.client.put(
            reverse(
                "details-update-delete-shirt",
                kwargs={
                    "version": kwargs["version"],
                    "pk": kwargs["id"]
                }
            ),
            data=kwargs["data"],
            content_type='application/json',
        )

    def add_a_shirt(self, **kwargs):
        return self.client.post(
            reverse(
                "create-list-shirt",
                kwargs={
                    "version": kwargs["version"]
                }
            ),
            data=kwargs["data"],
            content_type='application/json',
        )

    def delete_shirt(self, pk=0):
        return self.client.delete(
            reverse(
                "details-update-delete-shirt",
                kwargs={
                    "version": "v1",
                    "pk": pk
                }
            )
        )

    def setUp(self):
        # add test data
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@mail.com",
            password="testing",
            first_name="test",
            last_name="user",
        )
        self.add_shirt(name="name test", email="email1@test.com", size=20)
        self.add_shirt(name="name test 1", email="email2@test.com", size=22)


class GetAllShirtTest(BaseViewTest):

    def test_get_all_shirts(self):
        """
        This test ensures that all shirts added in the setUp method
        exist when we make a GET request to the shirt/ endpoint
        """
        self.login_client('admin', 'testing')
        # hit the API endpoint
        response = self.client.get(
            reverse("create-list-shirt", kwargs={"version": "v1"})
        )

        # fetch the data from db
        expected = Shirt.objects.all()
        serialized = ShirtSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetShirtDetailsTest(BaseViewTest):

    def test_get_shirt_details(self):
        """
        This test ensures that shirt details of a given id is
        returned
        """
        self.login_client('admin', 'testing')
        # hit the API endpoint
        response = self.get_shirt_details(1)
        # fetch the data from db
        expected = Shirt.objects.get(pk=1)
        serialized = ShirtSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a song that does not exist
        response = self.get_shirt_details(1000)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddShirtTest(BaseViewTest):

    def test_add_shirt(self):
        """
        This test ensures that a single shirt can be added
        """
        self.login_client('admin', 'testing')
        # hit the API endpoint
        response = self.add_a_shirt(
            version="v1",
            data=json.dumps({
                "name": "new name",
                "email": "new_user@email.com",
                "size": 10
            })
        )

        self.assertIn('id', response.data)
        response.data.pop('id')

        self.assertEqual(response.data, {
                "name": "new name",
                "email": "new_user@email.com",
                "size": 10
            })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.add_a_shirt(
            version="v1",
            data=json.dumps({
                "email": "new_user@email.com",
                "size": 10
            })
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateShirtTest(BaseViewTest):

    def test_update_shirt(self):
        """
        This test ensures that a single shirt can be updated.
        """
        self.login_client('admin', 'testing')
        # hit the API endpoint
        response = self.update_shirt(
            version="v1",
            id=2,
            data=json.dumps({
                "name": "name test xxx"
            })
        )

        # fetch the data from db
        expected = Shirt.objects.get(pk=2)
        serialized = ShirtSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with invalid data
        response = self.update_shirt(
            version="v1",
            id=200,
            data=json.dumps({
                "name": "name test xxx"
            })
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteShirtTest(BaseViewTest):

    def test_delete_shirt(self):
        """
        This test ensures that when a shirt of given id can be deleted
        """
        self.login_client('admin', 'testing')
        # hit the API endpoint
        response = self.delete_shirt(1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # test with invalid data
        response = self.delete_shirt(100)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
