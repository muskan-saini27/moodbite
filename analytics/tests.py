
from django.test import TestCase
from django.urls import reverse


class MoodBiteAnalyticsTests(TestCase):
    def test_analytics_dashboard_requires_authentication(self):
        response = self.client.get(reverse("analytics_dashboard"))
        self.assertIn(response.status_code, (301, 302, 303))

    def test_authenticated_user_can_open_analytics_dashboard(self):
        from django.contrib.auth.models import User

        user = User.objects.create_user(
            username="analytics_test_user",
            password="TestPassword123!",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("analytics_dashboard"))
        self.assertEqual(response.status_code, 200)

