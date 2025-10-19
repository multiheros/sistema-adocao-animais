from django import forms
from .models import Animal

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name', 'species', 'breed', 'age', 'description', 'image', 'adopted']
        labels = {
            'name': 'Nome',
            'species': 'Espécie',
            'breed': 'Raça',
            'age': 'Idade',
            'description': 'Descrição',
            'image': 'Imagem',
            'adopted': 'Adotado',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'species': forms.Select(attrs={'class': 'form-select text-uppercase'}),
            'breed': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'multiple': False, 'class': 'form-control'}),
            'adopted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostra um prompt em português ao invés de '---------'
        self.fields['species'].choices = [('', 'Selecione...')] + list(Animal.SPECIES_CHOICES)