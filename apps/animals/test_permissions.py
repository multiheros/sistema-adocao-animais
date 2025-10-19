from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.animals.models import Animal

User = get_user_model()


class AnimalPermissionsViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='p')
        self.other = User.objects.create_user(username='other', password='p')
        self.staff = User.objects.create_user(
            username='staff', password='p', is_staff=True
        )
        self.animal = Animal.objects.create(
            name='Bolt', species='dog', age=2, created_by=self.owner
        )

    def test_owner_can_edit(self):
        self.client.login(username='owner', password='p')
        url = reverse('animal_edit', args=[self.animal.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_non_owner_cannot_edit(self):
        self.client.login(username='other', password='p')
        url = reverse('animal_edit', args=[self.animal.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_staff_can_edit(self):
        self.client.login(username='staff', password='p')
        url = reverse('animal_edit', args=[self.animal.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_adopted_animal_cannot_be_edited(self):
        self.animal.adopted = True
        self.animal.save(update_fields=['adopted'])
        self.client.login(username='owner', password='p')
        url = reverse('animal_edit', args=[self.animal.pk])
        resp = self.client.get(url, follow=True)
        # Should redirect to detail with a warning message
        self.assertEqual(
            resp.redirect_chain[-1][0],
            reverse('animal_detail', args=[self.animal.pk]),
        )

    def test_owner_can_delete_confirm_page(self):
        self.client.login(username='owner', password='p')
        url = reverse('animal_delete', args=[self.animal.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_non_owner_cannot_delete(self):
        self.client.login(username='other', password='p')
        url = reverse('animal_delete', args=[self.animal.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_adopted_animal_cannot_be_deleted(self):
        self.animal.adopted = True
        self.animal.save(update_fields=['adopted'])
        self.client.login(username='owner', password='p')
        url = reverse('animal_delete', args=[self.animal.pk])
        resp = self.client.get(url, follow=True)
        self.assertEqual(
            resp.redirect_chain[-1][0],
            reverse('animal_detail', args=[self.animal.pk]),
        )
