from django.db import models
from django.conf import settings



class Animal(models.Model):
    SPECIES_CHOICES = [
        ('dog', 'Cachorro'),
        ('cat', 'Gato'),
        ('bird', 'Pássaro'),
        ('reptile', 'Réptil'),
        ('other', 'Outro'),
    ]

    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='animals/', blank=True, null=True)
    adopted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='animals_created'
    )

    def __str__(self):
        return self.name
