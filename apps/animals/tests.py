from django.test import TestCase
from .models import Animal

class AnimalModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Animal.objects.create(name="Buddy", species="Dog", age=3, description="Friendly dog looking for a home.")

    def test_animal_name(self):
        animal = Animal.objects.get(id=1)
        self.assertEqual(animal.name, "Buddy")

    def test_animal_species(self):
        animal = Animal.objects.get(id=1)
        self.assertEqual(animal.species, "Dog")

    def test_animal_age(self):
        animal = Animal.objects.get(id=1)
        self.assertEqual(animal.age, 3)

    def test_animal_description(self):
        animal = Animal.objects.get(id=1)
        self.assertEqual(animal.description, "Friendly dog looking for a home.")