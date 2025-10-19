from django.test import TestCase
from django.urls import reverse

class SmokeTests(TestCase):
    def test_home_redirects(self):
        resp = self.client.get('/')
        self.assertIn(resp.status_code, (200, 302))

    def test_animals_list(self):
        resp = self.client.get(reverse('animal_list'))
        self.assertEqual(resp.status_code, 200)

    def test_adoptions_list(self):
        resp = self.client.get(reverse('adoption_list'))
        self.assertEqual(resp.status_code, 200)

    def test_login_page(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)
