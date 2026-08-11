"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from appartements.views import (
    ajouter_paiement,
    detail_reservation,
    nettoyer_base_test,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('appartements.urls')),

    path(
    'depenses/',
    include('depenses.urls')
    ),

    path(
    "login/",
    auth_views.LoginView.as_view(
        template_name="registration/login.html"
    ),
    name="login"
    ),
    
    path(
            'reservation/<int:reservation_id>/',
            detail_reservation,
            name='detail_reservation'
        ),

    path(
        'reservation/<int:reservation_id>/paiement/',
        ajouter_paiement,
        name='ajouter_paiement'
    ),


    #path(
        #'admin/nettoyer-base-test/',
        #nettoyer_base_test,
        #name='nettoyer_base_test'
    #),
   

    

]
