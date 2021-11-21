import tempfile

from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from PIL import Image as PIL_Image

from .models import Image
from accounts.models import Account, Tier, Perk

client = APIClient()


class APITestCaseWithMedia(APITestCase):
    """
    class adds temporary directory for media files that gets deletes automatically after tests
    tests that uploads media should use:
    with self.settings(MEDIA_ROOT=self.temporary_dir.name):
    """
    temporary_dir = None

    @classmethod
    def setUpClass(cls):
        cls.temporary_dir = tempfile.TemporaryDirectory()

        super(APITestCaseWithMedia, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.temporary_dir = None
        super(APITestCaseWithMedia, cls).tearDownClass()


def get_temporary_image(temp_file, size, extension):
    color = (255, 0, 0, 0)
    image = PIL_Image.new("RGB", size, color)
    image.save(temp_file, extension)
    return temp_file


class GetAllImages(APITestCaseWithMedia):
    """
    Test getting list of all images belonging to requesting user
    """
    fixtures = ['accounts.json']

    def test_get_images_list_unauthorized(self):
        response = client.get(reverse('images-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_images_list_valid(self):
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            client.login(username='admin', password='admin')
            owner = User.objects.filter(username='admin').first()
            temp_file = tempfile.NamedTemporaryFile()
            test_image = get_temporary_image(temp_file, (200, 200), 'jpeg')
            file = InMemoryUploadedFile(test_image, None, test_image.name, 'image/jpeg', test_image.__sizeof__(), None)
            Image.objects.create(owner=owner, image=file)
            response = client.get(reverse('images-list'))
            client.logout()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Image.objects.all().count(), 1)
