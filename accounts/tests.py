
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class MoodBiteAuthenticationTests(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))
        self.assertIn(response.status_code, (301, 302, 303))

    def test_authenticated_user_can_open_profile(self):
        user = User.objects.create_user(
            username="moodbite_test_user",
            email="moodbite_test@example.com",
            password="TestPassword123!",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_registration_rejects_duplicate_username(self):
        User.objects.create_user(
            username="existing_user",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse("register"),
            {
                "username": "existing_user",
                "email": "new_user@example.com",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="existing_user").count(), 1)
