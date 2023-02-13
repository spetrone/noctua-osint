from django.test import TestCase, Client
from django.conf import settings
from http import HTTPStatus
from django.contrib.auth.models import User
from django.urls import reverse


# LOGIN TEST
class LoginTest(TestCase):
    #use an authorized client for testing
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.user.set_password('TESTPA$$1234')
        self.user.save()
        self.client = Client()

    def testLogin(self):
        response = self.client.post('/accounts/login/', data={'username': 'testuser', 'password': 'TESTPA$$1234'})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTemplateUsed('index.html')
        self.assertEqual(response["Location"], "/")

      
#authorized user tests
class AuthorizedUserIntergrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password="TESTPA$$1234")
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)

    #test index
    def test_get(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTemplateUsed('index.html')
        self.assertEqual(response["Location"], "dashboard/")

    #test diplaying account page
    def test_display_account(self):
        response = self.client.get(reverse("display_account"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed('account_profile.html')

    #test displaying the main dashboard
    def test_dashboard_access(self):
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed('index.html')

    #test user accessing page - "dash_query" - which is the main dashboard as well
    def test_dashboard_access(self):
        response = self.client.get(reverse("dash_query"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed('index.html')

    #test displaying the selection page (with no session data, should redirect
    # to main dashboard)
    def test_dashboard_access(self):
        response = self.client.get(reverse("dash_select"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], "/dashboard/dash_query/")
        self.assertTemplateUsed('index.html')

#LOGOUT TEST
class LogoutTest(TestCase):
    #use an authorized client for testing
    def setUp(self):
        self.user = User.objects.create(username='testuser', password="TESTPA$$1234")
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)

    def testLogout(self):
        response = self.client.post(path=reverse("logout"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse("login"))
      


#unauthorized user tests (not logged in)
class UnauthorizedUserIntegrationTests(TestCase):
#test index
    def test_get(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], "dashboard/") #settings.py
        self.assertTemplateUsed('login.html')

    #test diplaying account page
    def test_display_account(self):
        response = self.client.get(reverse("display_account"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTemplateUsed('login.html')
        self.assertRedirects(response, reverse("login") + "?next=/accounts/display_account/")

    #test displaying the main dashboard
    def test_dashboard_access(self):
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTemplateUsed('login.html')
        self.assertRedirects(response, reverse("login") + "?next=/dashboard/")

    #test user accessing page - "dash_query" - which is the main dashboard as well
    def test_dashboard_access(self):
        response = self.client.get(reverse("dash_query"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTemplateUsed('login.html')
        self.assertRedirects(response, reverse("login") + "?next=/dashboard/dash_query/")

    #test displaying the selection page (with no session data, should redirect
    # to main dashboard)
    def test_dashboard_access(self):
        response = self.client.get(reverse("dash_select"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTemplateUsed('login.html')
        self.assertRedirects(response, reverse("login") + "?next=/dashboard/dash_select/")

#USER CREATION TEST
class SignupTest(TestCase):
    #use an authorized client for testing
    def setUp(self):
        self.client = Client()

    def testSignup(self):
        response = self.client.post('/accounts/signup/', data={'username': 'testuser', 'password': 'TESTPA$$1234'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed('login.html')

        #test login with new user
        response = self.client.post('/accounts/login/', data={'username': 'testuser', 'password': 'TESTPA$$1234'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed('index.html')



