from django.shortcuts import render, redirect
from .models import Reservation, Appartement
from .forms import ReservationForm
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from .forms import AppartementForm
from .models import Appartement

from datetime import date, timedelta
from datetime import datetime

import qrcode
from io import BytesIO
from django.http import HttpResponse

from depenses.models import Depense

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from django.contrib.auth import logout
from django.shortcuts import redirect

from django.contrib.auth.decorators import user_passes_test
from .models import JournalActivite

from django.contrib.auth.models import User

#def liste_reservations(request):

    #recherche = request.GET.get('q')
    #appartement = request.GET.get('appartement')

    #reservations = Reservation.objects.all()

    #if recherche:
        #reservations = reservations.filter(
            #nom_client__icontains=recherche
        #)

    #if appartement:
        #reservations = reservations.filter(
            #appartement_id=appartement
        #)

    #total = reservations.aggregate(
        #Sum('net_a_payer')
    #)

    #appartements = Appartement.objects.all()

    #return render(
        #request,
        #'appartements/liste_reservations.html',
        #{
            #'reservations': reservations.order_by('-id'),
            #'total': total,
            #'appartements': appartements,
        #}
    #)


@login_required
@permission_required(
    'appartements.view_reservation',
    raise_exception=True
)
def liste_reservations(request):

    recherche = request.GET.get('q')
    appartement = request.GET.get('appartement')

    print("Recherche =", recherche)
    print("Appartement =", appartement)

    reservations = Reservation.objects.all()

    if recherche:
        reservations = reservations.filter(
            nom_client__icontains=recherche
        )

    print("Nombre trouvé =", reservations.count())

    if appartement:
        reservations = reservations.filter(
            appartement_id=appartement
        )

    total = reservations.aggregate(
        Sum('net_a_payer')
    )

    appartements = Appartement.objects.all()

    return render(
        request,
        'appartements/liste_reservations.html',
        {
            'reservations': reservations.order_by('-id'),
            'total': total,
            'appartements': appartements,
        }
    )



@login_required
def ajouter_reservation(request):

    if request.method == 'POST':
        form = ReservationForm(request.POST)

        if form.is_valid():

            reservation = form.save()

            enregistrer_activite(
                request,
                "Réservation",
                "Création",
                f"Réservation N°{reservation.id} créée pour {reservation.nom_client}"
            )

            return redirect('liste_reservations')

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

from django.db.models import Sum


@login_required
def dashboard(request):

    nb_appartements = Appartement.objects.count()

    nb_reservations = Reservation.objects.count()

    revenus = Reservation.objects.aggregate(
        Sum("net_a_payer")
    )

    depenses = Depense.objects.aggregate(
        Sum("montant")
    )

    total_revenus = revenus["net_a_payer__sum"] or 0
    total_depenses = depenses["montant__sum"] or 0

    benefice = total_revenus - total_depenses

    dernieres = Reservation.objects.order_by("-id")[:5]

    return render(
        request,
        "appartements/dashboard.html",
        {
            "nb_appartements": nb_appartements,
            "nb_reservations": nb_reservations,
            "revenus": revenus,
            "depenses": depenses,
            "benefice": benefice,
            "dernieres": dernieres,
        }
    )




@login_required
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
def rapport_financier(request):

    periode = request.GET.get("periode", "mois")
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    aujourd_hui = date.today()

    if periode == "jour":
        debut = fin = aujourd_hui

    elif periode == "semaine":
        debut = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin = debut + timedelta(days=6)

    elif periode == "annee":
        debut = date(aujourd_hui.year, 1, 1)
        fin = date(aujourd_hui.year, 12, 31)

    elif periode == "personnalise" and date_debut and date_fin:
        debut = date.fromisoformat(date_debut)
        fin = date.fromisoformat(date_fin)

    else:
        debut = date(aujourd_hui.year, aujourd_hui.month, 1)

        if aujourd_hui.month == 12:
            fin = date(aujourd_hui.year, 12, 31)
        else:
            fin = date(
                aujourd_hui.year,
                aujourd_hui.month + 1,
                1
            ) - timedelta(days=1)

    reservations = Reservation.objects.filter(
        date_arrivee__lte=fin,
        date_depart__gte=debut
    )

    depenses = Depense.objects.filter(
        date__range=[debut, fin]
    )

    total_revenus = reservations.aggregate(
        Sum("net_a_payer")
    )["net_a_payer__sum"] or 0

    total_depenses = depenses.aggregate(
        Sum("montant")
    )["montant__sum"] or 0

    benefice = total_revenus - total_depenses

    return render(
        request,
        "appartements/rapport_financier.html",
        {
            "reservations": reservations,
            "depenses": depenses,
            "revenus": total_revenus,
            "depenses_total": total_depenses,
            "benefice": benefice,
            "debut": debut,
            "fin": fin,
            "periode": periode,
        }
    )


from django.views.decorators.http import require_POST

@require_POST
def deconnexion(request):
    logout(request)
    return redirect("login")



@login_required
@user_passes_test(lambda u: u.is_superuser)
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
# Create your views here.
