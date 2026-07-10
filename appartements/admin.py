from django.contrib import admin
from .models import Appartement, Reservation


@admin.register(Appartement)
class AppartementAdmin(admin.ModelAdmin):
    list_display = (
        'nom',
        'prix_jour',
        'prix_mois'
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nom_client',
        'appartement',
        'type_location',
        'duree',
        'net_a_payer'
    )



from .models import JournalActivite

@admin.register(JournalActivite)
class JournalActiviteAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "utilisateur",
        "module",
        "action",
        "description",
    )

    list_filter = (
        "module",
        "action",
        "date",
    )

    search_fields = (
        "description",
        "utilisateur__username",
    )

# Register your models here.
