from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

    def test_dashboard_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard'), secure=True)
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_dashboard_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_threats_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('threats'), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_analytics_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('analytics'), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_network_scan_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('network_scan'), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_redis_status(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('redis_status'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())

    def test_celery_status(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('celery_status'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())

class SecurityTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_csrf_protection(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('dashboard'), {}, secure=True)
        self.assertEqual(response.status_code, 403)  # CSRF token missing

    def test_authentication_required(self):
        response = self.client.get(reverse('dashboard'), secure=True)
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_secure_headers(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('X-Frame-Options', response.headers)
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertIn('X-XSS-Protection', response.headers)
        self.assertIn('Content-Security-Policy', response.headers)
        self.assertIn('Strict-Transport-Security', response.headers)
