from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.animals.models import Animal
from apps.adoptions.models import Adoption

User = get_user_model()


class AdoptionRulesTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='u1', password='p')
        self.user2 = User.objects.create_user(username='u2', password='p')
        # species must be one of choices (dog/cat/bird/reptile/other)
        self.animal = Animal.objects.create(name='Rex', species='dog', age=3)

    def test_only_one_approved_per_animal(self):
        Adoption.objects.create(animal=self.animal, adopter=self.user1, status='approved')
        with self.assertRaises(ValidationError):
            # second approved should fail validation
            Adoption.objects.create(animal=self.animal, adopter=self.user2, status='approved')

    def test_adopted_flag_sync_on_status_change(self):
        a = Adoption.objects.create(animal=self.animal, adopter=self.user1, status='approved')
        self.animal.refresh_from_db()
        self.assertTrue(self.animal.adopted)
        # Changing to rejected should clear adopted if no other approved remain
        a.status = 'rejected'
        a.save()
        self.animal.refresh_from_db()
        self.assertFalse(self.animal.adopted)
