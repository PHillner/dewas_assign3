from django.test import TestCase
from django.test import Client
from models import Blog
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from datetime import datetime

# Create your tests here.

class BlogSiteTests(TestCase):

    def setUp(self):
        user1 = User.objects.create_user('user1','user1@test.com','pass1')
        user1.user_permissions.add(Permission.objects.get(codename='change_blog'))

        blog = Blog()
        blog.name = 'Test Name'
        blog.text = 'Test Text'
        blog.time = datetime.today()
        blog.save()

    def test_edit_not_logged_in(self):
        client = Client()
        response = client.get('/')
        print('Status code of "/" (not logged in): '+str(response.status_code))
        self.assertEqual(response.status_code, 200)

        response = client.get('/edit/1/', follow=True)
        print('Status code of "/edit/1/" (not logged in): '+str(response.status_code))
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response,'/login/?next=/edit/1/')



    def test_edit_logged_in(self):
        client = Client()
        response = client.get('/')
        print('Status code of "/" (logged in): '+str(response.status_code))
        self.assertEqual(response.status_code, 200)

        user1 = client.login(username='user1',password='pass1')
        self.assertIsNotNone(user1)

        client.get('/edit/1/')
        print('Status code of "/edit/1/" (logged in): '+str(response.status_code))
        self.assertEqual(response.status_code, 200)