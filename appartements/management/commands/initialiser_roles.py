from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from appartements.models import Appartement, Reservation
from depenses.models import Depense


class Command(BaseCommand):

    help = "Créer les groupes et leurs permissions"

    def handle(self, *args, **kwargs):

        admin, _ = Group.objects.get_or_create(
            name="Administrateur"
        )

        reception, _ = Group.objects.get_or_create(
            name="Réceptionniste"
        )

        comptable, _ = Group.objects.get_or_create(
            name="Comptable"
        )

        admin.permissions.set(
            Permission.objects.all()
        )

        reception.permissions.clear()

        reception.permissions.add(
            *Permission.objects.filter(
                content_type__in=[
                    ContentType.objects.get_for_model(Appartement),
                    ContentType.objects.get_for_model(Reservation),
                ]
            )
        )

        comptable.permissions.clear()

        comptable.permissions.add(
            *Permission.objects.filter(
                content_type=ContentType.objects.get_for_model(Depense)
            )
        )

        comptable.permissions.add(
            Permission.objects.get(
                codename="view_reservation"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Les rôles ont été créés avec succès."
            )
        )