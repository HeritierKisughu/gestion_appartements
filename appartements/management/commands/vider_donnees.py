from django.core.management.base import BaseCommand
from django.db import transaction

from appartements.models import (
    Appartement,
    Reservation,
    Paiement,
    JournalActivite,
)

try:
    from appartements.models import Depense
except ImportError:
    Depense = None


class Command(BaseCommand):

    help = "Supprime les données de test sans supprimer les utilisateurs."

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.WARNING(
                "Suppression des données métier..."
            )
        )

        # ==========================================
        # PAIEMENTS
        # ==========================================

        nombre_paiements = Paiement.objects.count()

        Paiement.objects.all().delete()

        self.stdout.write(
            f"Paiements supprimés : {nombre_paiements}"
        )

        # ==========================================
        # RÉSERVATIONS
        # ==========================================

        nombre_reservations = Reservation.objects.count()

        Reservation.objects.all().delete()

        self.stdout.write(
            f"Réservations supprimées : {nombre_reservations}"
        )

        # ==========================================
        # DÉPENSES
        # ==========================================

        if Depense:

            nombre_depenses = Depense.objects.count()

            Depense.objects.all().delete()

            self.stdout.write(
                f"Dépenses supprimées : {nombre_depenses}"
            )

        # ==========================================
        # JOURNAL D'ACTIVITÉ
        # ==========================================

        nombre_journaux = JournalActivite.objects.count()

        JournalActivite.objects.all().delete()

        self.stdout.write(
            f"Journaux supprimés : {nombre_journaux}"
        )

        # ==========================================
        # APPARTEMENTS
        # ==========================================

        nombre_appartements = Appartement.objects.count()

        Appartement.objects.all().delete()

        self.stdout.write(
            f"Appartements supprimés : {nombre_appartements}"
        )

        # ==========================================
        # FIN
        # ==========================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Base de données nettoyée avec succès."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Les utilisateurs et les groupes n'ont pas été supprimés."
            )
        )