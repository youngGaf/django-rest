from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from rest_framework_jwt.settings import api_settings
from rest_framework.reverse import reverse as api_reverse
from postings.models import BlogPost
User = get_user_model()

payload_handler = api_settings.JWT_PAYLOAD_HANDLER
encode_handler = api_settings.JWT_ENCODE_HANDLER


class BlogPostAPITestCase(APITestCase):
    def setUp(self):
        user_obj = User(username='gaf-testUser', email='gaf@testuser.com')
        user_obj.set_password('gaf-password')
        user_obj.save()
        blog_post = BlogPost.objects.create(user=user_obj,
                                            title='test title',
                                            content='test content')

    def test_single_user(self):
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_single_post(self):
        post_count = BlogPost.objects.count()
        self.assertEqual(post_count, 1)

    def test_get_list(self):
        data = {}
        url = api_reverse('api-postings:post-listcreate')
        response = self.client.get(url, data, format('json'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_item(self):
        data = {'title': 'this is new test', 'content': 'getting contents ready'}
        url = api_reverse('api-postings:post-listcreate')
        response = self.client.post(url, data, format('json'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_item(self):
        blog_post = BlogPost.objects.first()
        data = {}
        url = blog_post.get_api_url()
        response = self.client.get(url, data, format('json'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item(self):
        blog_post = BlogPost.objects.first()
        data = {'title': 'this is old test', 'content': 'getting contents ready'}
        url = blog_post.get_api_url()
        response = self.client.post(url, data, format('json'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.put(url, data, format('json'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_item_with_user(self):
        blog_post = BlogPost.objects.first()
        data = {'title': 'this is old test', 'content': 'getting contents ready'}
        url = blog_post.get_api_url()
        user = User.objects.first()
        payload = payload_handler(user)
        token_rsp = encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_rsp)  # JWT <token>

        response = self.client.put(url, data, format('json'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_item_with_user(self):
        data = {'title': 'this is new test', 'content': 'getting contents ready'}
        url = api_reverse('api-postings:post-listcreate')
        user = User.objects.first()
        payload = payload_handler(user)
        token_rsp = encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_rsp)

        response = self.client.post(url, data, format('json'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_ownership(self):
        owner = User.objects.create(username='testUser2')
        blog_post = BlogPost.objects.create(user=owner,
                                            title='test title',
                                            content='test content')
        user = User.objects.first()
        self.assertNotEqual(owner.username, user.username)

        data = {'title': 'this is new test', 'content': 'getting contents ready'}
        payload = payload_handler(user)
        token_rsp = encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_rsp)
        url = blog_post.get_api_url()

        response = self.client.put(url, data, format('json'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #  Using manual login <jwt token>
    def test_user_login_and_update(self):
        data = {
            'username': 'gaf-testUser',
            'password': 'gaf-password'
        }
        url = api_reverse('api-login')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get('token')

        if token is not None:
            blog_post = BlogPost.objects.first()
            data = {'title': 'this is old test', 'content': 'getting contents ready'}
            url = blog_post.get_api_url()
            self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
            response = self.client.put(url, data, format('json'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
