from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum

from .models import Depense
from .forms import DepenseForm
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required(
    'depenses.view_depense',
    raise_exception=True
)
def liste_depenses(request):

    recherche = request.GET.get("q")
    categorie = request.GET.get("categorie")
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    depenses = Depense.objects.all()

    if recherche:
        depenses = depenses.filter(
            libelle__icontains=recherche
        )

    if categorie:
        depenses = depenses.filter(
            categorie=categorie
        )

    if date_debut:
        depenses = depenses.filter(
            date__gte=date_debut
        )

    if date_fin:
        depenses = depenses.filter(
            date__lte=date_fin
        )

    total = depenses.aggregate(
        Sum("montant")
    )

    return render(
        request,
        "depenses/liste_depenses.html",
        {
            "depenses": depenses.order_by("-date"),
            "total": total,
            "categories": Depense.CATEGORIES,
        }
    )

@login_required
def ajouter_depense(request):

    if request.method == "POST":

        form = DepenseForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "liste_depenses"
            )

    else:

        form = DepenseForm()

    return render(
        request,
        "depenses/depense_form.html",
        {
            "form": form
        }
    )

@login_required
def modifier_depense(request, pk):

    depense = get_object_or_404(
        Depense,
        pk=pk
    )

    if request.method == "POST":

        form = DepenseForm(
            request.POST,
            instance=depense
        )

        if form.is_valid():

            form.save()

            return redirect(
                "liste_depenses"
            )

    else:

        form = DepenseForm(
            instance=depense
        )

    return render(
        request,
        "depenses/depense_form.html",
        {
            "form": form
        }
    )

@login_required
def supprimer_depense(request, pk):

    depense = get_object_or_404(
        Depense,
        pk=pk
    )

    depense.delete()

    return redirect(
        "liste_depenses"
    )

@login_required
def imprimer_depenses(request):

    recherche = request.GET.get("q")
    categorie = request.GET.get("categorie")
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    depenses = Depense.objects.all()

    if recherche:
        depenses = depenses.filter(
            libelle__icontains=recherche
        )

    if categorie:
        depenses = depenses.filter(
            categorie=categorie
        )

    if date_debut:
        depenses = depenses.filter(
            date__gte=date_debut
        )

    if date_fin:
        depenses = depenses.filter(
            date__lte=date_fin
        )

    total = depenses.aggregate(
        Sum("montant")
    )

    return render(
        request,
        "depenses/imprimer_depenses.html",
        {
            "depenses": depenses.order_by("-date"),
            "total": total,
            "date_debut": date_debut,
            "date_fin": date_fin,
            "categorie": categorie,
            "recherche": recherche,
        }
    )