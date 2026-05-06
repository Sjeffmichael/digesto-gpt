from django.test import TestCase, Client
from django.urls import reverse
from apps.user_authentication.models import User

class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "auth@example.com"
        self.password = "securepassword"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_user_creation(self):
        """Test that a user is created correctly."""
        self.assertEqual(self.user.email, self.email)
        self.assertTrue(self.user.check_password(self.password))
        self.assertFalse(self.user.is_admin)

    def test_superuser_creation(self):
        """Test that a superuser is created correctly."""
        admin_user = User.objects.create_superuser(email="admin@example.com", password="password")
        self.assertTrue(admin_user.is_admin)
        self.assertTrue(admin_user.is_staff)

    def test_login_view(self):
        """Test the login functionality."""
        url = reverse('authentication:login')
        response = self.client.post(url, {
            'username': self.email, # LoginForm probably uses 'username' field mapping to email
            'password': self.password
        })
        # Since it's HTMX, it might return a special header or status
        # In this project, it returns HttpResponseClientRedirect
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header('HX-Redirect'))

    def test_registration_view(self):
        """Test the registration functionality."""
        url = reverse('authentication:register')
        response = self.client.post(url, {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
