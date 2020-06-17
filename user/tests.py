import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.core.files.uploadedfile import SimpleUploadedFile

from user.serializers import UserSerializer, UserWithoutPasswordSerializer

User = get_user_model()


# tests for models
class UserModelTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user', password='test_password', first_name='first',
                                        last_name='last', profile_picture=SimpleUploadedFile(name='captcha1.jpg',
                                                                                             content=open(
                                                                                                 'pictures/test/test_image.jpg',
                                                                                                 'rb').read(),
                                                                                             content_type='image/jpeg'))

    def test_user(self):
        """"
        This test ensures that the user created in the setup
        exists
        """
        users = User.objects.all()

        self.assertEqual(self.user.username, users[0].username)
        self.assertEqual(self.user.password, users[0].password)
        self.assertEqual(self.user.first_name, users[0].first_name)
        self.assertEqual(self.user.last_name, users[0].last_name)
        self.assertEqual(self.user.profile_picture, users[0].profile_picture)


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_user(username, password, first_name, last_name, email, profile_picture):
        User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name,
                                 profile_picture=profile_picture, email=email)

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

    def login_a_user(self, username, password):
        url = reverse(
            "token_obtain_pair"
        )
        return self.client.post(
            url,
            data=json.dumps({
                "username": username,
                "password": password
            }),
            content_type="application/json"
        )

    def get_user_details(self, pk=0):
        return self.client.get(
            reverse(
                "user-details",
                kwargs={
                    "version": "v1",
                    "pk": pk
                }
            )
        )

    def update_user(self, **kwargs):
        return self.client.put(
            reverse(
                "user-update",
                kwargs={
                    "version": kwargs["version"],
                    "pk": kwargs["id"]
                }
            ),
            data=kwargs["data"],
            format='multipart',
        )

    def register_user(self, username, password, email, first_name, last_name, profile_picture):
        data = {
            'username': username,
            'password': password,
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        }

        if profile_picture:
            data['profile_picture'] = profile_picture

        return self.client.post(
            reverse(
                "user-register",
                kwargs={
                    "version": "v1"
                }
            ),
            data=data,
            format='multipart'
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
        self.create_user(username='test_user', password='test_password', first_name='first', last_name='last',
                         email="email1@test.com",
                         profile_picture=SimpleUploadedFile(name='captcha1.jpg',
                                                            content=open('pictures/test/test_image.jpg', 'rb').read(),
                                                            content_type='image/jpeg'))
        self.create_user(username='test_user1', password='test_password1', first_name='first1', last_name='last1',
                         email="email2@test.com",
                         profile_picture=SimpleUploadedFile(name='captcha2.jpg',
                                                            content=open('pictures/test/test_image.jpg', 'rb').read(),
                                                            content_type='image/jpeg'))


class GetAllUsersTest(BaseViewTest):

    def test_get_all_users(self):
        """
        This test ensures that all users added in the setUp method
        exist when we make a GET request to the users/ endpoint
        """
        # hit the API endpoint
        response = self.client.get(
            reverse("user-list", kwargs={"version": "v1"})
        )
        # fetch the data from db
        expected = User.objects.all()
        serialized = UserSerializer(expected, many=True)

        for i in range(len(serialized.data)):
            expected_picture = serialized.data[i].pop('profile_picture')
            picture_from_response = response.data[i].pop('profile_picture')

            # pop password, since we don't return password from our API
            serialized.data[i].pop('password')

            self.assertEqual(serialized.data[i], response.data[i])

            if expected_picture:
                assert expected_picture in picture_from_response

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthLoginUserTest(BaseViewTest):
    """
    Tests for the login endpoint
    """

    def test_login_user(self):
        # test login with valid credentials
        response = self.login_a_user("admin", "testing")
        # assert access key exists
        self.assertIn("access", response.data)
        # assert refresh key exists
        self.assertIn("refresh", response.data)
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test login with invalid credentials
        response = self.login_a_user("anonymous", "pass")
        # assert status code is 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthRegisterUserTest(BaseViewTest):
    """
    Tests for auth/register/ endpoint
    """

    def test_register_user(self):
        profile_picture = SimpleUploadedFile(name='profile_pic.jpg',
                                             content=open('pictures/test/test_image.jpg', 'rb').read(),
                                             content_type='image/jpeg')
        response = self.register_user("new_user", "new_pass", "new_user@mail.com", "first", "last", profile_picture)
        # assert status code is 201 CREATED
        self.assertEqual(response.data["username"], "new_user")
        self.assertEqual(response.data["email"], "new_user@mail.com")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test with invalid data
        response = self.register_user("", "", "", "", "", None)
        # assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetUserDetailsTest(BaseViewTest):

    def test_get_user_details(self):
        """
        This test ensures that a single user of a given id is
        returned
        """
        # hit the API endpoint
        response = self.get_user_details(1)
        # fetch the data from db
        expected = User.objects.get(pk=1)
        serialized = UserWithoutPasswordSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test with a user that does not exist
        response = self.get_user_details(1000)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateUserTest(BaseViewTest):

    def test_update_user(self):
        """
        This test ensures that a single song can be updated. In this
        test we update the second song in the db with valid data and
        the third song with invalid data and make assertions
        """
        # Unauthorized user should be got error message
        # hit the API endpoint
        response = self.update_user(
            version="v1",
            id=1,
            data={
                'last_name': 'lastname'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # User should not be able to update another user data
        self.login_client('test_user', 'test_password')
        # hit the API endpoint
        response = self.update_user(
            version="v1",
            id=3,
            data={
                'last_name': 'lastname'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Admin should be able to update another user data
        self.login_client('admin', 'testing')

        profile_picture = SimpleUploadedFile(name='profile_pic1.jpg',
                                             content=open('pictures/test/test_image.jpg', 'rb').read(),
                                             content_type='image/jpeg')
        # hit the API endpoint
        response = self.update_user(
            version="v1",
            id=3,
            data={
                'last_name': 'lastname',
                'profile_picture': profile_picture
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User should be able to update their own data
        self.login_client('test_user', 'test_password')

        profile_picture = SimpleUploadedFile(name='profile_pic2.jpg',
                                             content=open('pictures/test/test_image.jpg', 'rb').read(),
                                             content_type='image/jpeg')
        # hit the API endpoint
        response = self.update_user(
            version="v1",
            id=2,
            data={
                'last_name': 'lastname',
                'profile_picture': profile_picture
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
