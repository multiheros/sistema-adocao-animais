from django import forms
from .models import Adoption

class AdoptionForm(forms.ModelForm):
    class Meta:
        model = Adoption
        fields = ['animal', 'adopter', 'status']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select'}),
            'adopter': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select text-uppercase'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Por padrão, usuários comuns não podem escolher adotante nem status
        if user and not (user.is_staff or user.is_superuser):
            self.fields['adopter'].disabled = True
            self.fields['status'].disabled = True
            self.fields['adopter'].widget.attrs['readonly'] = True
            self.fields['status'].widget.attrs['readonly'] = True