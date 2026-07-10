from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    #path('', views.liste_reservations, name='liste_reservations'),
    path('', views.dashboard, name='dashboard'),

    path(
    'reservations/',
    views.liste_reservations,
    name='liste_reservations'
    ),

    path('nouvelle/', views.ajouter_reservation, name='ajouter_reservation'),
    path(
    'facture/<int:pk>/',
    views.facture,
    name='facture'
    ),

    path(
    'qr-facture/<int:pk>/',
    views.qr_facture,
    name='qr_facture'
    ),

    path(
    'modifier/<int:pk>/',
    views.modifier_reservation,
    name='modifier_reservation'
    ),

    path(
    'supprimer/<int:pk>/',
    views.supprimer_reservation,
    name='supprimer_reservation'
    ),

    path(
    'appartements/',
    views.liste_appartements,
    name='liste_appartements'
    ),

    path(
        'appartements/nouveau/',
        views.ajouter_appartement,
        name='ajouter_appartement'
    ),

    path(
        'appartements/modifier/<int:pk>/',
        views.modifier_appartement,
        name='modifier_appartement'
    ),

    path(
        'appartements/supprimer/<int:pk>/',
        views.supprimer_appartement,
        name='supprimer_appartement'
    ),

    path(
    'rapport-mensuel/',
    views.rapport_mensuel,
    name='rapport_mensuel'
    ),

    path(
    "rapport-financier/",
    views.rapport_financier,
    name="rapport_financier"
    ),

    path(
    "logout/",
    views.deconnexion,
    name="logout"
    ),
    

    path(
    "journal/",
    views.journal_activite,
    name="journal_activite"
    ),
    
]
