from django.db import models
from django.core.exceptions import ValidationError

class Appartement(models.Model):
    nom = models.CharField(max_length=100)
    prix_jour = models.DecimalField(max_digits=10, decimal_places=2)
    prix_mois = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom
    

class Reservation(models.Model):

    TYPE_LOCATION = (
        ('jour', 'Par Jour'),
        ('mois', 'Par Mois'),
    )

    date = models.DateField(auto_now_add=True)

    nom_client = models.CharField(max_length=200)

    date_reservation = models.DateField()

    appartement = models.ForeignKey(
        Appartement,
        on_delete=models.PROTECT
    )

    type_location = models.CharField(
        max_length=10,
        choices=TYPE_LOCATION
    )

    date_arrivee = models.DateField()

    date_depart = models.DateField()

    duree = models.IntegerField(default=0)


    montant_location = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )


    autres_frais = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )

    net_a_payer = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    def clean(self):
        reservations = Reservation.objects.filter(
            appartement=self.appartement
        )

        if self.pk:
            reservations = reservations.exclude(
                pk=self.pk
            )

        for reservation in reservations:

            if (
                self.date_arrivee <= reservation.date_depart
                and
                self.date_depart >= reservation.date_arrivee
            ):
                raise ValidationError(
                    "❌ Cet appartement est déjà réservé pour cette période."
                )




    def save(self, *args, **kwargs):

        self.full_clean()

        if self.type_location == 'jour':

            self.duree = (
                self.date_depart -
                self.date_arrivee
            ).days

            prix = self.appartement.prix_jour



        else:

            mois = (
                (self.date_depart.year - self.date_arrivee.year) * 12
                +
                (self.date_depart.month - self.date_arrivee.month)
            )

            # Si le jour de départ est supérieur ou égal au jour d'arrivée,
            # on compte un mois supplémentaire.
            if self.date_depart.day >= self.date_arrivee.day:
                mois += 1

            # Minimum : 1 mois
            if mois <= 0:
                mois = 1

            self.duree = mois

            prix = self.appartement.prix_mois




        # Sécurité : au moins 1 jour/mois
        if self.duree <= 0:
            self.duree = 1

        # Montant de la location (sans autres frais)
        self.montant_location = prix * self.duree

        # Total à payer
        self.net_a_payer = (
            self.montant_location +
            self.autres_frais
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.nom_client}"
    


from django.contrib.auth.models import User

class JournalActivite(models.Model):

    date = models.DateTimeField(auto_now_add=True)

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    module = models.CharField(max_length=100)

    action = models.CharField(max_length=50)

    description = models.TextField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.utilisateur} - {self.action}"
    

# Create your models here.
