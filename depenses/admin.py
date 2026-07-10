from django.contrib import admin
from .models import Depense


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):

    list_display = (
        'date',
        'libelle',
        'categorie',
        'montant',
    )

    search_fields = (
        'libelle',
    )

    list_filter = (
        'categorie',
    )