from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import (
    Reservation,
    Appartement,
    JournalActivite
)

from .middleware import get_current_user

@receiver(post_save, sender=Reservation)
def journal_reservation(sender, instance, created, **kwargs):

    utilisateur = get_current_user()

    if not utilisateur or not utilisateur.is_authenticated:
        return

    JournalActivite.objects.create(

        utilisateur=utilisateur,

        module="Réservations",

        action="Création" if created else "Modification",

        description=f"Réservation N°{instance.id}"

    )

@receiver(post_delete, sender=Reservation)
def journal_reservation_delete(sender, instance, **kwargs):

    utilisateur = get_current_user()

    if not utilisateur or not utilisateur.is_authenticated:
        return

    JournalActivite.objects.create(

        utilisateur=utilisateur,

        module="Réservations",

        action="Suppression",

        description=f"Réservation N°{instance.id}"

    )