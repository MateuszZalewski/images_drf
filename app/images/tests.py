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
    tests that uploads media must use:
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

    def _get_temporary_image(self, size, extension):
        """
        creates NamedTemporaryFile and stores image created with PIL in it
        :param size: (height, width) tuple
        :param extension: file extension eg. 'jpeg'
        :return: NamedTemporaryFile object
        """
        color = (255, 0, 0)
        image = PIL_Image.new("RGB", size, color)
        temp_file = tempfile.NamedTemporaryFile()
        image.save(temp_file, extension)
        return temp_file

    def _create_image(self, auth, size=(200, 200)):
        """
        need to be invoked inside:
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
        :param auth: username, password iterable
        :param size: height, width tuple
        :return: newly created Image tuple
        """
        client.login(username=auth[0], password=auth[1])
        owner = User.objects.filter(username=auth[0]).first()
        test_image = self._get_temporary_image(size, 'jpeg')
        file = InMemoryUploadedFile(test_image, None, test_image.name, 'image/jpeg', test_image.__sizeof__(), None)
        Image.objects.create(owner=owner, image=file)
        client.logout()


class GetAllImages(APITestCaseWithMedia):
    """
    Test getting list of all images belonging to requesting user
    """
    fixtures = ['accounts.json']

    def test_get_images_list_unauthorized(self):
        """
        request images list as unauthorized user
        """
        response = client.get(reverse('images-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_images_list_valid(self):
        """
        create two images one of them owned by 'admin'. Then get list of all images owned by 'admin'
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'))
            self._create_image(('admin', 'admin'))

            client.login(username='admin', password='admin')
            response = client.get(reverse('images-list'))
            client.logout()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(Image.objects.all().count(), 2)
