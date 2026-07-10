from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.liste_depenses,
        name='liste_depenses'
    ),

    path(
        'nouvelle/',
        views.ajouter_depense,
        name='ajouter_depense'
    ),

    path(
    'modifier/<int:pk>/',
    views.modifier_depense,
    name='modifier_depense'
    ),

    path(
        'supprimer/<int:pk>/',
        views.supprimer_depense,
        name='supprimer_depense'
    ),

    path(
        "imprimer/",
        views.imprimer_depenses,
        name="imprimer_depenses"
    ),

]