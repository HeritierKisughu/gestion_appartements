from django.db import models


class Depense(models.Model):

    CATEGORIES = (
        ('EAU', 'Eau'),
        ('ELECTRICITE', 'Électricité'),
        ('ENTRETIEN', 'Entretien'),
        ('INTERNET', 'Internet'),
        ('SALAIRE', 'Salaire'),
        ('TRANSPORT', 'Transport'),
        ('APPROVISIONNEMENT', 'Approvisionnement'),
        ('AUTRE', 'Autre'),
    )

    date = models.DateField()

    libelle = models.CharField(
        max_length=200
    )

    categorie = models.CharField(
        max_length=30,
        choices=CATEGORIES
    )

    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    observation = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.libelle