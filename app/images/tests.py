import io
import tempfile

from PIL import Image as PIL_Image
from django.contrib.auth.models import User
from django.core.files.base import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Image, ExpiringLink

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

    def _get_temporary_image(self, size, extension='jpeg', temp_file=None):
        """
        creates NamedTemporaryFile and stores image created with PIL in it
        :param size: (height, width) tuple
        :param extension: file extension eg. 'jpeg'
        :return: NamedTemporaryFile object
        """
        color = (255, 0, 0)
        image = PIL_Image.new("RGB", size, color)
        if temp_file is None:
            temp_file = tempfile.NamedTemporaryFile()
        image.save(temp_file, extension)
        temp_file.seek(0)
        return temp_file

    def _create_image(self, auth, size=(200, 200)):
        """
        need to be invoked inside:
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
        :param auth: username, password iterable
        :param size: height, width tuple
        :return: newly created Image
        """
        client.login(username=auth[0], password=auth[1])
        owner = User.objects.filter(username=auth[0]).first()
        test_image = self._get_temporary_image(size, 'jpeg')
        file = InMemoryUploadedFile(test_image, None, test_image.name, 'image/jpeg', test_image.__sizeof__(), None)
        image = Image.objects.create(owner=owner, image=file)
        client.logout()
        return image


class ExpiringLinksTest(APITestCaseWithMedia):
    """
    Test creating and using expiring links to images
    """
    fixtures = ['accounts.json']

    def test_fetch_expiring_invalid_time(self):
        """
        Try to fetch expiring link to image with invalid time parameter
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('sunshine', 'YUsPygfgf8rLaU7'))
            client.login(username='sunshine', password='YUsPygfgf8rLaU7')
            response = client.get(reverse('create-expiring', args=[image.image.name, 299]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fetch_expiring_link_valid(self):
        """
        Fetch expiring link to your own image with 'expiring link' perk assigned to your account tier
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('sunshine', 'YUsPygfgf8rLaU7'))
            client.login(username='sunshine', password='YUsPygfgf8rLaU7')
            response = client.get(reverse('create-expiring', args=[image.image.name, 300]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = client.get(response.json()['link'])
            img_bytes = next(response.streaming_content)
            pil_image = PIL_Image.open(io.BytesIO(img_bytes))
            self.assertEqual(pil_image.size, (200, 200))

    def test_fetch_expiring_link_invalid_perks(self):
        """
        Fetch expiring link to your own image without 'expiring link' perk assigned to your account tier
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'))
            client.login(username='seamel', password='ZwpDu9BGHRTTqKX')
            response = client.get(reverse('create-expiring', args=[image.image.name, 300]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(ExpiringLink.objects.all().count(), 0)


class PostImageTest(APITestCaseWithMedia):
    """
    Test uploading image
    """
    fixtures = ['accounts.json']

    def test_upload_unauthorized(self):
        """
        Try uploading image without authorization
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            file = io.BytesIO()
            pil_image = self._get_temporary_image((200, 200), 'jpeg', file)
            data = {
                'image': File(pil_image, 'name.jpg')
            }

            response = client.post(reverse('images-list'), data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(Image.objects.all().count(), 0)

    def test_upload_valid_jpeg(self):
        """
        Test uploading valid jpeg image
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            file = io.BytesIO()
            pil_image = self._get_temporary_image((200, 200), 'jpeg', file)
            client.login(username='admin', password='admin')
            data = {
                'image': File(pil_image, 'name.jpg')
            }

            response = client.post(reverse('images-list'), data)
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Image.objects.all().count(), 1)

    def test_upload_valid_png(self):
        """
        Test uploading valid png image
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            file = io.BytesIO()
            pil_image = self._get_temporary_image((200, 200), 'png', file)
            client.login(username='admin', password='admin')
            data = {
                'image': File(pil_image, 'name.png')
            }

            response = client.post(reverse('images-list'), data)
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Image.objects.all().count(), 1)

    def test_upload_bmp(self):
        """
        Try uploading bmp image. Server should only accept jpeg and png.
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            file = io.BytesIO()
            pil_image = self._get_temporary_image((200, 200), 'bmp', file)
            client.login(username='admin', password='admin')
            data = {
                'image': File(pil_image, 'name.bmp')
            }

            response = client.post(reverse('images-list'), data)
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Image.objects.all().count(), 0)

    def test_upload_image_too_big(self):
        """
        Try uploading image that is too big
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            file = io.BytesIO()
            pil_image = self._get_temporary_image((10_000, 24_000), 'jpeg', file)
            client.login(username='admin', password='admin')
            data = {
                'image': File(pil_image, 'name.jpeg')
            }
            response = client.post(reverse('images-list'), data)
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Image.objects.all().count(), 0)


class GetImageTest(APITestCaseWithMedia):
    """
    Test getting image
    """
    fixtures = ['accounts.json']

    def test_get_image_unauthorized(self):
        """
        Try to get image without authorization
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'))
            response = client.get(reverse('media', args=[image.image.name]))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_image_without_perk(self):
        """
        Try getting image without 'original image' perk
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'))
            client.login(username='seamel', password='ZwpDu9BGHRTTqKX')
            response = client.get(reverse('media', args=[image.image.name]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_image_valid(self):
        """
        Test getting your image with 'original image' perk
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('sunshine', 'YUsPygfgf8rLaU7'), (333, 443))
            client.login(username='sunshine', password='YUsPygfgf8rLaU7')
            response = client.get(reverse('media', args=[image.image.name]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            img_bytes = next(response.streaming_content)
            pil_image = PIL_Image.open(io.BytesIO(img_bytes))
            self.assertEqual(pil_image.size, (333, 443))

    def test_get_another_user_image(self):
        """
        Try to get a picture of another user with the 'original image' perk
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'), (333, 443))
            client.login(username='sunshine', password='YUsPygfgf8rLaU7')
            response = client.get(reverse('media', args=[image.image.name]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetThumbnailTest(APITestCaseWithMedia):
    """
    Test getting image thumbnail
    """
    fixtures = ['accounts.json']

    def test_get_thumbnail_unauthorized(self):
        """
        Try to get thumbnail without authorization
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'))
            response = client.get(reverse('thumbnail', args=[image.image.name, 400]))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_thumbnail_valid(self):
        """
        Test getting thumbnail as owner with necessary perks
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'), (300, 300))
            client.login(username='seamel', password='ZwpDu9BGHRTTqKX')
            response = client.get(reverse('thumbnail', args=[image.image.name, 200]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            img_bytes = next(response.streaming_content)
            pil_image = PIL_Image.open(io.BytesIO(img_bytes))
            self.assertEqual(pil_image.size, (200, 200))

    def test_get_thumbnail_with_original_size_valid(self):
        """
        Test getting thumbnail with the same height as the original size.
        User have perk to request thumbnail of this height but dont have perk to request original image
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'), (200, 200))
            client.login(username='seamel', password='ZwpDu9BGHRTTqKX')
            response = client.get(reverse('thumbnail', args=[image.image.name, 200]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            img_bytes = next(response.streaming_content)
            pil_image = PIL_Image.open(io.BytesIO(img_bytes))
            self.assertEqual(pil_image.size, (200, 200))

    def test_get_thumbnail_invalid_perks(self):
        """
        Test getting a thumbnail with a height you do not have permission to access
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'))
            client.login(username='seamel', password='ZwpDu9BGHRTTqKX')
            response = client.get(reverse('thumbnail', args=[image.image.name, 400]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_thumbnail_as_staff_user(self):
        """
        Test access to another user's image thumbnail as staff user
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('seamel', 'ZwpDu9BGHRTTqKX'), (700, 700))
            client.login(username='admin', password='admin')
            response = client.get(reverse('thumbnail', args=[image.image.name, 666]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            img_bytes = next(response.streaming_content)
            pil_image = PIL_Image.open(io.BytesIO(img_bytes))
            self.assertEqual(pil_image.size, (666, 666))

    def test_get_another_user_thumbnail(self):
        """
        Test access to another user's image thumbnail as regular user with valid perks
        """
        with self.settings(MEDIA_ROOT=self.temporary_dir.name):
            image = self._create_image(('admin', 'admin'), (700, 700))
            client.login(username='seamel', password='ZwpDu9BGHRTTqKX')
            response = client.get(reverse('thumbnail', args=[image.image.name, 200]))
            client.logout()
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetAllImagesTest(APITestCaseWithMedia):
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
