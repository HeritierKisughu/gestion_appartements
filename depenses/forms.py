from django import forms
from .models import Depense


class DepenseForm(forms.ModelForm):

    class Meta:
        model = Depense
        fields = "__all__"

        widgets = {

            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'libelle': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'categorie': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'montant': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'observation': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            ),

        }