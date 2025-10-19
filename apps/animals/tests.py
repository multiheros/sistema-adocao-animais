from django.test import TestCase
from .models import Animal

class AnimalModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # species must match choices: dog/cat/bird/reptile/other
        Animal.objects.create(
            name="Buddy", species="dog", age=3,
            description="Friendly dog looking for a home."
        )

    def test_animal_name(self):
        animal = Animal.objects.get(id=1)
        self.assertEqual(animal.name, "Buddy")

    def test_animal_species(self):
        animal = Animal.objects.get(id=1)
        self.assertEqual(animal.species, "dog")

    def test_animal_age(self):
        animal = Animal.objects.get(id=1)
        self.assertEqual(animal.age, 3)

    def test_animal_description(self):
        animal = Animal.objects.get(id=1)
        self.assertEqual(animal.description, "Friendly dog looking for a home.")