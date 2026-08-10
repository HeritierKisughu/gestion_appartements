from django.shortcuts import render, redirect, get_object_or_404
from .models import Reservation, Appartement, Paiement
from .forms import AppartementForm, ReservationForm, PaiementForm

from django.db.models import Sum


from datetime import date, timedelta
from datetime import datetime

import qrcode
from io import BytesIO
from django.http import HttpResponse

from depenses.models import Depense

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from django.contrib.auth import logout

from django.contrib.auth.decorators import user_passes_test
from .models import JournalActivite

from django.contrib.auth.models import User

from .utils import enregistrer_activite

from decimal import Decimal

from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from .decorators import role_requis

    


@login_required
@permission_required(
    'appartements.view_reservation',
    raise_exception=True
)


@login_required
def liste_reservations(request):

    recherche = request.GET.get('q')
    appartement = request.GET.get('appartement')


    # =====================================================
    # RÉSERVATIONS
    # =====================================================

    reservations = Reservation.objects.all()


    # Recherche client

    if recherche:

        reservations = reservations.filter(
            nom_client__icontains=recherche
        )


    # Filtre appartement

    if appartement:

        reservations = reservations.filter(
            appartement_id=appartement
        )


    # =====================================================
    # LISTE DES RÉSERVATIONS
    # =====================================================

    reservations = list(
        reservations
        .select_related('appartement')
        .prefetch_related('paiements')
        .order_by('-id')
    )


    # =====================================================
    # CALCULS PAIEMENTS
    # =====================================================

    total_reservations = Decimal('0.00')

    total_paye_general = Decimal('0.00')


    for reservation in reservations:

        # Total de la réservation

        total_reservations += reservation.net_a_payer


        # Total des paiements

        total_paye = sum(

            (
                paiement.montant
                for paiement in reservation.paiements.all()
            ),

            Decimal('0.00')
        )


        # Reste à payer

        reste_a_payer = (
            reservation.net_a_payer
            - total_paye
        )


        # Sécurité

        if reste_a_payer < Decimal('0.00'):

            reste_a_payer = Decimal('0.00')


        # Statut

        if total_paye <= Decimal('0.00'):

            statut_paiement = 'IMPAYÉ'

        elif total_paye < reservation.net_a_payer:

            statut_paiement = 'PARTIELLEMENT PAYÉ'

        else:

            statut_paiement = 'PAYÉ'


        # Ajout des valeurs à l'objet réservation

        reservation.total_paye = total_paye

        reservation.reste_a_payer = reste_a_payer

        reservation.statut_paiement = statut_paiement


        # Total général payé

        total_paye_general += total_paye


    # =====================================================
    # RESTE GÉNÉRAL
    # =====================================================

    reste_general = (
        total_reservations
        - total_paye_general
    )


    if reste_general < Decimal('0.00'):

        reste_general = Decimal('0.00')


    # =====================================================
    # APPARTEMENTS
    # =====================================================

    appartements = Appartement.objects.all()


    # =====================================================
    # AFFICHAGE
    # =====================================================

    return render(

        request,

        'appartements/liste_reservations.html',

        {
            'reservations': reservations,

            'total_reservations': total_reservations,

            'total_paye_general': total_paye_general,

            'reste_general': reste_general,

            'appartements': appartements,
        }

    )

@login_required
def ajouter_reservation(request):

    if request.method == 'POST':
        form = ReservationForm(request.POST)

        import traceback

        if form.is_valid():

            try:

                reservation = form.save()

                enregistrer_activite(
                    request,
                    "Réservation",
                    "Création",
                    f"Réservation N°{reservation.id} créée pour {reservation.nom_client}"
                )

                return redirect("liste_reservations")

            except Exception as e:

                print("=" * 80)
                print("ERREUR RESERVATION")
                traceback.print_exc()
                print("=" * 80)

                raise

    else:
        form = ReservationForm()

    appartements = Appartement.objects.all()

    return render(
        request,
        'appartements/reservation_form.html',
        {
            'form': form,
            'appartements': appartements
        }
    )

total = Reservation.objects.aggregate(
    Sum('net_a_payer')
)


@login_required
def facture(request, pk):

    reservation = get_object_or_404(
        Reservation,
        pk=pk
    )

    return render(
        request,
        'appartements/facture.html',
        {
            'reservation': reservation
        }
    )



@login_required
def modifier_reservation(request, pk):

    reservation = get_object_or_404(
        Reservation,
        pk=pk
    )

    if request.method == 'POST':

        form = ReservationForm(
            request.POST,
            instance=reservation
        )

        if form.is_valid():
            form.save()

            return redirect(
                'liste_reservations'
            )

    else:

        form = ReservationForm(
            instance=reservation
        )

    appartements = Appartement.objects.all()

    return render(
        request,
        'appartements/reservation_form.html',
        {
            'form': form,
            'appartements': appartements
        }
    )


@login_required
def supprimer_reservation(request, pk):

    reservation = get_object_or_404(
        Reservation,
        pk=pk
    )

    reservation.delete()

    return redirect(
        'liste_reservations'
    )


@login_required
@permission_required(
    'appartements.view_appartement',
    raise_exception=True
)
def liste_appartements(request):

    appartements = Appartement.objects.all().order_by('nom')

    return render(
        request,
        'appartements/liste_appartements.html',
        {
            'appartements': appartements
        }
    )


@login_required
def ajouter_appartement(request):

    if request.method == 'POST':

        form = AppartementForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('liste_appartements')

    else:
        form = AppartementForm()

    return render(
        request,
        'appartements/appartement_form.html',
        {
            'form': form
        }
    )



@login_required
def modifier_appartement(request, pk):

    appartement = get_object_or_404(
        Appartement,
        pk=pk
    )

    if request.method == 'POST':

        form = AppartementForm(
            request.POST,
            instance=appartement
        )

        if form.is_valid():
            form.save()

            return redirect(
                'liste_appartements'
            )

    else:

        form = AppartementForm(
            instance=appartement
        )

    return render(
        request,
        'appartements/appartement_form.html',
        {
            'form': form
        }
    )


@login_required
def supprimer_appartement(request, pk):

    appartement = get_object_or_404(
        Appartement,
        pk=pk
    )

    appartement.delete()

    return redirect(
        'liste_appartements'
    )


@login_required
def dashboard(request):

    aujourd_hui = date.today()

    appartements = Appartement.objects.all()

    appartements_occupes = []
    appartements_libres = []

    # =====================================================
    # OCCUPATION / DISPONIBILITÉ
    # =====================================================

    for appartement in appartements:

        # Réservation actuellement en cours
        reservation_actuelle = (
            Reservation.objects
            .filter(
                appartement=appartement,
                date_arrivee__lte=aujourd_hui,
                date_depart__gte=aujourd_hui,
            )
            .order_by('date_depart')
            .first()
        )

        # =================================================
        # APPARTEMENT OCCUPÉ
        # =================================================

        if reservation_actuelle:

            appartement.reservation_actuelle = reservation_actuelle

            # Prochaine réservation après la réservation actuelle
            prochaine_reservation = (
                Reservation.objects
                .filter(
                    appartement=appartement,
                    date_arrivee__gt=reservation_actuelle.date_depart
                )
                .order_by('date_arrivee')
                .first()
            )

            appartement.prochaine_reservation = prochaine_reservation

            appartements_occupes.append(appartement)

        # =================================================
        # APPARTEMENT LIBRE
        # =================================================

        else:

            prochaine_reservation = (
                Reservation.objects
                .filter(
                    appartement=appartement,
                    date_arrivee__gte=aujourd_hui
                )
                .order_by('date_arrivee')
                .first()
            )

            appartement.prochaine_reservation = prochaine_reservation

            appartements_libres.append(appartement)


    # =====================================================
    # STATISTIQUES
    # =====================================================

    nombre_total = appartements.count()

    nombre_occupes = len(appartements_occupes)

    nombre_libres = len(appartements_libres)


    if nombre_total > 0:

        taux_occupation = round(
            (nombre_occupes / nombre_total) * 100,
            2
        )

    else:

        taux_occupation = 0


    # =====================================================
    # CONTEXTE
    # =====================================================

    context = {

        'appartements_occupes': appartements_occupes,

        'appartements_libres': appartements_libres,

        'nombre_total': nombre_total,

        'nombre_occupes': nombre_occupes,

        'nombre_libres': nombre_libres,

        'taux_occupation': taux_occupation,

        'aujourd_hui': aujourd_hui,

    }


    # =====================================================
    # CONTRÔLE DES DONNÉES FINANCIÈRES
    # =====================================================

    groupes = list(
        request.user.groups.values_list(
            'name',
            flat=True
        )
    )


    peut_voir_finances = (

        request.user.is_superuser

        or 'Administrateur' in groupes

        or 'Comptable' in groupes

    )


    if peut_voir_finances:

        reservations = Reservation.objects.all()


        # =================================================
        # TOTAL DES RÉSERVATIONS
        # =================================================

        total_reservations = (

            reservations.aggregate(
                total=Sum('net_a_payer')
            )['total']

            or Decimal('0.00')

        )


        # =================================================
        # TOTAL PAYÉ
        # =================================================

        total_paye = (

            reservations.aggregate(
                total=Sum('paiements__montant')
            )['total']

            or Decimal('0.00')

        )


        # =================================================
        # RESTE À ENCAISSER
        # =================================================

        reste_a_encaisser = (
            total_reservations
            - total_paye
        )


        if reste_a_encaisser < 0:

            reste_a_encaisser = Decimal('0.00')


        context.update({

            'peut_voir_finances': True,

            'total_reservations': total_reservations,

            'total_paye': total_paye,

            'reste_a_encaisser': reste_a_encaisser,

        })

    else:

        context['peut_voir_finances'] = False


    return render(

        request,

        'appartements/dashboard.html',

        context

    )



@login_required
@role_requis('Administrateur', 'Comptable')
def rapport_mensuel(request):

    mois = request.GET.get('mois')

    reservations = Reservation.objects.all()

    if mois:
        reservations = reservations.filter(
            date_reservation__month=mois
        )

    total = reservations.aggregate(
        Sum('net_a_payer')
    )

    return render(
        request,
        'appartements/rapport_mensuel.html',
        {
            'reservations': reservations,
            'total': total,
            'mois': mois,
        }
    )



@login_required
def qr_facture(request, pk):

    reservation = get_object_or_404(
        Reservation,
        pk=pk
    )

    numero = (
        f"FAC-{reservation.date_reservation.year}-"
        f"{reservation.id:06d}"
    )

    contenu = f"""
Facture : {numero}

Client : {reservation.nom_client}

Appartement : {reservation.appartement}

Montant : {reservation.net_a_payer}$

Date : {reservation.date_reservation}
"""

    qr = qrcode.make(contenu)

    buffer = BytesIO()

    qr.save(buffer, format="PNG")

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/png"
    )


@login_required
@role_requis('Administrateur', 'Comptable')
def rapport_financier(request):

    periode = request.GET.get("periode", "mois")
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    aujourd_hui = date.today()

    # =====================================================
    # DÉTERMINATION DE LA PÉRIODE
    # =====================================================

    if periode == "jour":

        debut = fin = aujourd_hui

    elif periode == "semaine":

        debut = aujourd_hui - timedelta(
            days=aujourd_hui.weekday()
        )

        fin = debut + timedelta(days=6)

    elif periode == "annee":

        debut = date(
            aujourd_hui.year,
            1,
            1
        )

        fin = date(
            aujourd_hui.year,
            12,
            31
        )

    elif (
        periode == "personnalise"
        and date_debut
        and date_fin
    ):

        debut = date.fromisoformat(date_debut)
        fin = date.fromisoformat(date_fin)

    else:

        # MOIS EN COURS

        debut = date(
            aujourd_hui.year,
            aujourd_hui.month,
            1
        )

        if aujourd_hui.month == 12:

            fin = date(
                aujourd_hui.year,
                12,
                31
            )

        else:

            fin = (
                date(
                    aujourd_hui.year,
                    aujourd_hui.month + 1,
                    1
                )
                - timedelta(days=1)
            )


    # =====================================================
    # RÉSERVATIONS
    # =====================================================

    reservations = Reservation.objects.filter(
        date_reservation__range=[
            debut,
            fin
        ]
    ).select_related(
        'appartement'
    )


    # =====================================================
    # PAIEMENTS
    # =====================================================

    paiements = Paiement.objects.filter(
        date_paiement__date__range=[
            debut,
            fin
        ]
    ).select_related(
        'reservation',
        'reservation__appartement'
    )


    # =====================================================
    # DÉPENSES
    # =====================================================

    depenses = Depense.objects.filter(
        date__range=[
            debut,
            fin
        ]
    )


    # =====================================================
    # TOTAL DES RÉSERVATIONS
    # =====================================================

    total_reservations = (

        reservations.aggregate(
            total=Sum("net_a_payer")
        )["total"]

        or Decimal("0.00")
    )


    # =====================================================
    # TOTAL ENCAISSÉ
    # =====================================================

    total_paye = (

        paiements.aggregate(
            total=Sum("montant")
        )["total"]

        or Decimal("0.00")
    )


    # =====================================================
    # RESTE À ENCAISSER
    #
    # Attention :
    # ce reste concerne les réservations enregistrées
    # pendant la période sélectionnée.
    # =====================================================

    paiements_reservations = (

        Paiement.objects.filter(
            reservation__in=reservations
        ).aggregate(
            total=Sum("montant")
        )["total"]

        or Decimal("0.00")
    )


    reste_a_encaisser = (
        total_reservations
        - paiements_reservations
    )


    if reste_a_encaisser < 0:

        reste_a_encaisser = Decimal("0.00")


    # =====================================================
    # TOTAL DÉPENSES
    # =====================================================

    total_depenses = (

        depenses.aggregate(
            total=Sum("montant")
        )["total"]

        or Decimal("0.00")
    )


    # =====================================================
    # SOLDE DE TRÉSORERIE
    #
    # Argent réellement encaissé
    # moins les dépenses réellement enregistrées.
    # =====================================================

    solde_tresorerie = (
        total_paye
        - total_depenses
    )


    # =====================================================
    # CONTEXTE
    # =====================================================

    context = {

        "reservations": reservations,

        "paiements": paiements,

        "depenses": depenses,

        "revenus": total_reservations,

        "total_reservations": total_reservations,

        "total_paye": total_paye,

        "reste_a_encaisser": reste_a_encaisser,

        "depenses_total": total_depenses,

        "solde_tresorerie": solde_tresorerie,

        "debut": debut,

        "fin": fin,

        "periode": periode,

    }


    return render(
        request,
        "appartements/rapport_financier.html",
        context
    )


from django.views.decorators.http import require_POST

@require_POST
def deconnexion(request):
    logout(request)
    return redirect("login")



@login_required
@role_requis('Administrateur')
def journal_activite(request):

    journaux = JournalActivite.objects.all()


    journaux = JournalActivite.objects.select_related('utilisateur').all()

    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    utilisateur = request.GET.get('utilisateur')
    module = request.GET.get('module')
    q = request.GET.get('q')

    if date_debut:
        journaux = journaux.filter(date__date__gte=date_debut)

    if date_fin:
        journaux = journaux.filter(date__date__lte=date_fin)

    if utilisateur:
        journaux = journaux.filter(utilisateur_id=utilisateur)

    if module:
        journaux = journaux.filter(module=module)

    if q:
        journaux = journaux.filter(description__icontains=q)


    context = {
        "journaux": journaux,

        'utilisateurs': User.objects.all(),
        'modules': JournalActivite.objects.values_list(
            'module', flat=True
        ).distinct(),
    }

    return render(
        request,
        "journal_activite.html",
        context
    )



@login_required
@role_requis('Administrateur', 'Comptable')
def ajouter_paiement(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    paiements = reservation.paiements.all()

    total_paye = sum(
        paiement.montant
        for paiement in paiements
    )

    reste_a_payer = (
        reservation.net_a_payer - total_paye
    )

    if reste_a_payer < 0:
        reste_a_payer = 0


    # =========================
    # ENREGISTREMENT DU PAIEMENT
    # =========================

    if request.method == 'POST':

        form = PaiementForm(request.POST)

        if form.is_valid():

            paiement = form.save(commit=False)

            paiement.reservation = reservation

            # Vérification du montant
            if paiement.montant > reste_a_payer:

                form.add_error(
                    'montant',
                    f"Le montant ne peut pas dépasser "
                    f"le reste à payer de "
                    f"{reste_a_payer:.2f} $."
                )

            else:

                paiement.save()

                enregistrer_activite(
                    request,
                    "Paiement",
                    "Création",
                    f"Paiement de {paiement.montant:.2f} $ "
                    f"pour la réservation N°{reservation.id}"
                )

                return redirect(
                    'detail_reservation',
                    reservation_id=reservation.id
                )


    # =========================
    # AFFICHAGE DU FORMULAIRE
    # =========================

    else:

        form = PaiementForm(
            initial={
                'montant': reste_a_payer
            }
        )


    return render(
        request,
        'appartements/paiement_form.html',
        {
            'form': form,
            'reservation': reservation,
            'total_paye': total_paye,
            'reste_a_payer': reste_a_payer,
        }
    )



@login_required
def detail_reservation(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    paiements = reservation.paiements.all()

    total_paye = sum(
        paiement.montant
        for paiement in paiements
    )

    reste_a_payer = (
        reservation.net_a_payer - total_paye
    )

    if total_paye <= 0:
        statut = "IMPAYÉ"

    elif total_paye < reservation.net_a_payer:
        statut = "PARTIELLEMENT PAYÉ"

    else:
        statut = "PAYÉ"

    return render(
        request,
        'appartements/detail_reservation.html',
        {
            'reservation': reservation,
            'paiements': paiements,
            'total_paye': total_paye,
            'reste_a_payer': max(reste_a_payer, 0),
            'statut': statut,
        }
    )
# Create your views here.
