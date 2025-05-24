from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class UserActivationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123",
            is_active=False,
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_activate_user_success(self):
        url = reverse("activate-user", kwargs={"uid": self.uid, "token": self.token})
        response = self.client.get(url)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)
        self.assertIn("Account activated", response.data["detail"])

    def test_activate_user_invalid_token(self):
        invalid_token = "wrong-token"
        url = reverse("activate-user", kwargs={"uid": self.uid, "token": invalid_token})
        response = self.client.get(url)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)
        self.assertIn("Invalid token", response.data["detail"])

    def test_activate_user_invalid_uid(self):
        url = reverse("activate-user", kwargs={"uid": "invalid", "token": self.token})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid UID", response.data["detail"])
