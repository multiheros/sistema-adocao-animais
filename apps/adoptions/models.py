from django.db import models
from django.conf import settings
from apps.animals.models import Animal
from django.core.exceptions import ValidationError

class Adoption(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='adoptions')
    adopter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='adoptions')
    adoption_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendente'),
        ('approved', 'Aprovada'),
        ('rejected', 'Rejeitada'),
    ], default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['animal'], condition=models.Q(status='approved'), name='unique_approved_adoption_per_animal')
        ]

    def __str__(self):
        return f"{self.adopter} -> {self.animal} ({self.status})"

    def clean(self):
        # Se tentando aprovar, certifique-se que não há outra aprovada
        if self.status == 'approved':
            exists = Adoption.objects.filter(animal=self.animal, status='approved')
            if self.pk:
                exists = exists.exclude(pk=self.pk)
            if exists.exists():
                raise ValidationError('Este animal já possui uma adoção aprovada.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Sincroniza o flag adopted do Animal
        animal = self.animal
        if self.status == 'approved' and not animal.adopted:
            animal.adopted = True
            animal.save(update_fields=['adopted'])
        elif self.status != 'approved':
            # Se nenhuma adoção permanece aprovada, desmarca adotado
            if not Adoption.objects.filter(animal=animal, status='approved').exists() and animal.adopted:
                animal.adopted = False
                animal.save(update_fields=['adopted'])