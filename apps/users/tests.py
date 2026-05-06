from django.test import TestCase, Client
from django.urls import reverse
from apps.user_authentication.models import User

class UserListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(email="admin@example.com", password="password")
        self.client.login(email="admin@example.com", password="password")
        self.user = User.objects.create_user(email="user@example.com", password="password")
        self.url = reverse('users:users-section')

    def test_user_list_view(self):
        """Test that the user list is accessible to admin."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user@example.com")

    def test_user_detail_view(self):
        """Test that user detail is accessible."""
        url = reverse('users:user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_delete(self):
        """Test that a user can be deleted (soft delete)."""
        url = reverse('users:delete-user', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
