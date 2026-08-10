from django import forms
from .models import Appartement, Reservation, Paiement

class AppartementForm(forms.ModelForm):
    class Meta:
        model = Appartement
        fields = '__all__'

class ReservationForm(forms.ModelForm):

    class Meta:
        model = Reservation
        fields = [
            'nom_client',
            'date_reservation',
            'appartement',
            'type_location',
            'date_arrivee',
            'date_depart',
            'autres_frais',
        ]

        widgets = {
            'date_reservation': forms.DateInput(attrs={'type': 'date'}),
            'date_arrivee': forms.DateInput(attrs={'type': 'date'}),
            'date_depart': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):

        cleaned_data = super().clean()

        appartement = cleaned_data.get('appartement')
        date_arrivee = cleaned_data.get('date_arrivee')
        date_depart = cleaned_data.get('date_depart')

        if appartement and date_arrivee and date_depart:

            conflit = Reservation.objects.filter(
                appartement=appartement,
                date_arrivee__lt=date_depart,
                date_depart__gt=date_arrivee
            )

            # Permet la modification sans conflit avec lui-même
            if self.instance.pk:
                conflit = conflit.exclude(
                    pk=self.instance.pk
                )

            if conflit.exists():
                raise forms.ValidationError(
                    "Cet appartement est déjà réservé pendant cette période."
                )

        return cleaned_data


class PaiementForm(forms.ModelForm):

    class Meta:
        model = Paiement

        fields = [
            'montant',
            'mode_paiement',
            'reference',
            'observation',
        ]

        widgets = {

            'montant': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0.01',
                    'placeholder': 'Montant payé'
                }
            ),

            'mode_paiement': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'reference': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Référence du paiement (facultatif)'
                }
            ),

            'observation': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Observation (facultatif)'
                }
            ),
        }