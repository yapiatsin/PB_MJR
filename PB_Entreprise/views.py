from datetime import date, datetime, time, timedelta, timezone, timedelta
import json
from typing import Any
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView,CreateView, UpdateView, TemplateView
from django.contrib import messages
import pandas as pd
from userauths.models import *
from .models import *
from .forms import *
from django.contrib.auth import logout
from django.db.models import Count
from django.db.models import Sum,F
import calendar
from django.db.models.functions import ExtractMonth
from django.db.models.functions import Coalesce
# Create your views here.
from .forms import DateForm
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from userauths.mixins import CustomPermissionRequiredMixin
from django.views.decorators.http import require_POST
from calendar import monthrange
from calendar import SUNDAY
from django.utils.timezone import now

from django.core.mail import send_mail
from userauths.utils import search_vehicules

def permission_denied_view(request, exception):
    return render(request, 'no_acces.html',status=403)

def custom_404_view(request, exception):
    return render(request, 'error.html',status=404)

def temp_arr(request):
    # return render(request, 'perfect/dashboard.html')
    return render(request, 'perfect/tmp_arr.html')

def base(request):
    # return render(request, 'perfect/dashboard.html')
    return render(request, 'perfect/base.html')

class ResumeView(TemplateView):
    template_name = 'pbent/resume_to_day.html'

class CarFluxView(TemplateView):
    model = Vehicule
    template_name = 'perfect/car_flux.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicule = Vehicule.objects.all()
        context={
            'vehicule':vehicule,
        }
        return context

class CarFluxDetailsView(DetailView):
    model = Vehicule
    form_class = DateForm
    template_name = 'perfect/car_flux.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        vehicule = Vehicule.objects.all()
        vehi = self.get_object()
    #-----------------------------------Pour Faire les filtre selon les dates entrées---------------------------------
        form = self.form_class(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            
            ################################----Recettes----#############################
            total_recettes = Recette.objects.filter(vehicule=vehi, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piec_echange= PiecEchange.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_charg_admin = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_admin = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            
            #-------------------------------------------------------------------------------------------------------------------------------
            total_reparation = Reparation.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparation =Reparation.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_piece= Piece.objects.filter(reparation__in = total_reparation, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piece= Piece.objects.filter(reparation__in = list_reparation, date_saisie__range=[date_debut, date_fin])
            
            total_assurances = Assurance.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurance = Assurance.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_visite = VisiteTechnique.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_visite = VisiteTechnique.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_entretien = Entretien.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_entretien = Entretien.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_patente = Patente.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(vehicule=vehi,date_saisie__range=[date_debut, date_fin])
            
            total_vignette = Vignette.objects.filter(vehicule=vehi, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_vignette = Vignette.objects.filter(vehicule=vehi, date_saisie__range=[date_debut, date_fin])
            
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
        else:
            ################################----Recettes----#############################
            total_recettes = Recette.objects.filter(vehicule=vehi, date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piec_echange= PiecEchange.objects.filter(vehicule=vehi,date_saisie=date.today())
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_fix = ChargeFixe.objects.filter(vehicule=vehi,date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_charg_var = ChargeVariable.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_var = ChargeVariable.objects.filter(vehicule=vehi,date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_charg_admin = ChargeVariable.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_admin = ChargeVariable.objects.filter(vehicule=vehi,date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_reparation = Reparation.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparation =Reparation.objects.filter(vehicule=vehi,date_saisie=date.today())
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(reparation__in = list_reparation,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piece= Piece.objects.filter(reparation__in = list_reparation,date_saisie=date.today())
            
            total_assurances = Assurance.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurance = Assurance.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            total_visite = VisiteTechnique.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_visite = VisiteTechnique.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            total_entretien = Entretien.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_entretien = Entretien.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            total_patente = Patente.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(vehicule=vehi,date_saisie=date.today())
            
            total_vignette = Vignette.objects.filter(vehicule=vehi,date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_vignette = Vignette.objects.filter(vehicule=vehi,date_saisie=date.today())
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            
        context={
            'car':vehi,
            'vehicule':vehicule,
            'total_recettes':total_recettes,
            
            'total_charg':total_charg,
            'taux_marge_format':taux_marge_format,
            'taux_marge':taux_marge,
            'total_piece':total_piece,
            'list_piece':list_piece,
            
            'total_piec_echange':total_piec_echange,
            'list_piec_echange':list_piec_echange,
            
            'total_charg_fix':total_charg_fix,
            'list_charg_fix':list_charg_fix,
            
            'total_charg_var':total_charg_var,
            'list_charg_var':list_charg_var,
            
            'total_charg_admin':total_charg_admin,
            'list_charg_admin':list_charg_admin,
            
            'total_reparation':total_reparation,
            'list_reparation':list_reparation,
            
            'total_assurances':total_assurances,
            'list_assurance':list_assurance,
            
            'total_visite':total_visite,
            'list_visite':list_visite,
            
            'total_entretien':total_entretien,
            'list_entretien':list_entretien,
            
            'total_patente':total_patente,
            'list_patente':list_patente,
            'total_vignette':total_vignette,
            'list_vignette':list_vignette,
            
            'labels':label,
            'form':form,
            'dates':dates
        }
        return context
    
class Bilanday(TemplateView):
    form_class = DateForm
    template_name = 'perfect/bilan_day.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
#-----------------------------------Pour Faire les filtre selon les dates entrées---------------------------------
        form = self.form_class(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
            ################################----Recettes----#############################
            total_recettes_vtc = Recette.objects.filter(vehicule__category__category='VTC',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            list_recettes_vtc = Recette.objects.filter(vehicule__category__category='VTC',date_saisie__range=[date_debut, date_fin])
            
            total_recettes_taxi = Recette.objects.filter(vehicule__category__category='TAXI',date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            list_recettes_taxi = Recette.objects.filter(vehicule__category__category='TAXI',date_saisie__range=[date_debut, date_fin])
            total_recettes = total_recettes_vtc + total_recettes_taxi
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piece= Piece.objects.filter(date_saisie__range=[date_debut, date_fin])
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piec_echange= PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_charg_admin = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_admin = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            
            #-------------------------------------------------------------------------------------------------------------------------------
            total_reparation = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparation =Reparation.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_assurances = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurance = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_visite = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_visite = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_entretien = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_entretien = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_patente = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_vignette = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_vignette = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_encaissement = Encaissement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_encaissement = Encaissement.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            total_decaissement = Decaissement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            list_decaissement = Decaissement.objects.filter(date_saisie__range=[date_debut, date_fin])
            
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
           
        else:
            catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
            ################################----Recettes----#############################
            total_recettes_vtc = Recette.objects.filter(vehicule__category__category='VTC', date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
            list_recettes_vtc = Recette.objects.filter(vehicule__category__category='VTC', date_saisie=date.today())
            
            total_recettes_taxi = Recette.objects.filter(vehicule__category__category='TAXI', date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
            list_recettes_taxi = Recette.objects.filter(vehicule__category__category='TAXI', date_saisie=date.today())
            total_recettes = total_recettes_vtc + total_recettes_vtc
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piece= Piece.objects.filter(date_saisie=date.today())
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_piec_echange= PiecEchange.objects.filter(date_saisie=date.today())
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_fix = ChargeFixe.objects.filter(date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_charg_var = ChargeVariable.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_var = ChargeVariable.objects.filter(date_saisie=date.today())
            #-------------------------------------------------------------------------------------------------------------------------------
            total_charg_admin = ChargeVariable.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_charg_admin = ChargeVariable.objects.filter(date_saisie=date.today())
            
            #-------------------------------------------------------------------------------------------------------------------------------
            total_reparation = Reparation.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_reparation =Reparation.objects.filter(date_saisie=date.today())
            
            total_assurances = Assurance.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_assurance = Assurance.objects.filter(date_saisie=date.today())
            
            total_visite = VisiteTechnique.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_visite = VisiteTechnique.objects.filter(date_saisie=date.today())
            
            total_entretien = Entretien.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_entretien = Entretien.objects.filter(date_saisie=date.today())
            
            total_patente = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_patente = Patente.objects.filter(date_saisie=date.today())
            
            total_vignette = Vignette.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_vignette = Vignette.objects.filter(date_saisie=date.today())
            
            total_encaissement = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_encaissement = Encaissement.objects.filter(date_saisie=date.today())
            
            total_decaissement = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            list_decaissement = Decaissement.objects.filter(date_saisie=date.today())
            
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            
        context={
            'total_recettes_taxi':total_recettes_taxi,
            'list_recettes_taxi':list_recettes_taxi,
            'total_recettes_vtc':total_recettes_vtc,
            'list_recettes_vtc':list_recettes_vtc,
            
            'total_recettes':total_recettes,
            'total_piece':total_piece,
            'list_piece':list_piece,
            
            'total_piec_echange':total_piec_echange,
            'list_piec_echange':list_piec_echange,
            
            'total_charg_fix':total_charg_fix,
            'list_charg_fix':list_charg_fix,
            
            'total_charg_var':total_charg_var,
            'list_charg_var':list_charg_var,
            
            'total_charg_admin':total_charg_admin,
            'list_charg_admin':list_charg_admin,
            
            'total_reparation':total_reparation,
            'list_reparation':list_reparation,
            
            'total_assurances':total_assurances,
            'list_assurance':list_assurance,
            
            'total_visite':total_visite,
            'list_visite':list_visite,
            
            'total_entretien':total_entretien,
            'list_entretien':list_entretien,
            
            'total_patente':total_patente,
            'list_patente':list_patente,
            
            'total_vignette':total_vignette,
            'list_vignette':list_vignette,
            
            'total_encaissement':total_encaissement,
            'list_encaissement':list_encaissement,
            
            'total_decaissement':total_decaissement,
            'list_decaissement':list_decaissement,
            
            'labels':label,
            'form':form,
            'dates':dates
        }
        return context

class TableaustopView(CustomPermissionRequiredMixin,TemplateView):
    model = Vehicule
    permission_url = 'temps'
    template_name = "perfect/temp_arret.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get month and year from the request; default to the current month and year
        month = self.request.GET.get('month', timezone.now().month)
        year = self.request.GET.get('year', timezone.now().year)
        # Convert month and year to integers
        month = int(month)
        year = int(year)
        days_in_month = monthrange(year, month)[1]
        month_name = datetime(year, month, 1).strftime("%B")
        # vehicules = Vehicule.objects.all()
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        context['current_date'] = date.today()
        total_actions_sum = 0
        total_cost_parts_sum = 0
        total_income_sum = 0
        total_piece_sum = 0
        
        total_visit_sum = 0
        total_panne_sum = 0
        total_accident_sum = 0
        total_autrarret_sum = 0
        
        total_visitechique_sum = 0 
        total_entretien_sum = 0 
        
        total_repairs_by_motifs = 0 
        total_motif_arrets = 0 
        
        vehicule_data = []
        for vehicule in vehicules:
            total_actions = (
                Entretien.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count() +
                VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count() +
                Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count() +
                Reparation.objects.filter(vehicule=vehicule,motif="Visite", date_saisie__month=month, date_saisie__year=year).count() +
                Reparation.objects.filter(vehicule=vehicule,motif="Panne", date_saisie__month=month, date_saisie__year=year).count() +
                Reparation.objects.filter(vehicule=vehicule,motif="Accident", date_saisie__month=month, date_saisie__year=year).count()
            )
            total_cost_parts = Piece.objects.filter(
                reparation__vehicule=vehicule, date_saisie__month=month, date_saisie__year=year
            ).aggregate(total_cost=models.Sum('montant'))['total_cost'] or 0

            total_income = Recette.objects.filter(
                vehicule=vehicule, date_saisie__month=month, date_saisie__year=year
            ).aggregate(total_income=models.Sum('montant'))['total_income'] or 0

            part_details_queryset = Piece.objects.filter(
                reparation__vehicule=vehicule, date_saisie__month=month, date_saisie__year=year
            ).values('libelle').annotate(count=models.Count('libelle'), total_price=models.Sum('montant'))
            
            all_piece = Piece.objects.filter(reparation__vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()
            all_visitechnique = VisiteTechnique.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()
            all_entretien = Entretien.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()

            part_details = "; ".join(
                f"{part['libelle']} ({part['count']}) {part['total_price']}" for part in part_details_queryset
            )

            daily_actions = [0] * days_in_month
            for day in range(1, days_in_month + 1):
                for model in [Reparation, VisiteTechnique, Entretien, Autrarret]:
                    count = model.objects.filter(
                        vehicule=vehicule, date_saisie__day=day, date_saisie__month=month, date_saisie__year=year
                    ).count()
                    daily_actions[day - 1] += count
            
            repairs_by_motif = {
                'P-vis': Reparation.objects.filter(vehicule=vehicule, motif="Visite", date_saisie__month=month, date_saisie__year=year).count(),
                'pan': Reparation.objects.filter(vehicule=vehicule, motif="Panne", date_saisie__month=month, date_saisie__year=year).count(),
                'acc': Reparation.objects.filter(vehicule=vehicule, motif="Accident", date_saisie__month=month, date_saisie__year=year).count(),
            }
            total_repairs_by_motif = (
                Reparation.objects.filter(vehicule=vehicule, motif="Visite", date_saisie__month=month, date_saisie__year=year).count()+
                Reparation.objects.filter(vehicule=vehicule, motif="Panne", date_saisie__month=month, date_saisie__year=year).count()+
                Reparation.objects.filter(vehicule=vehicule, motif="Accident", date_saisie__month=month, date_saisie__year=year).count()
            )
            motif_arret = {
                'vis': VisiteTechnique.objects.filter(vehicule=vehicule,date_saisie__month=month, date_saisie__year=year).count(),
                'ent': Entretien.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count(),
                'aut': Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count(),
            }
            total_motif_arret = (
                VisiteTechnique.objects.filter(vehicule=vehicule,date_saisie__month=month, date_saisie__year=year).count()+
                Entretien.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()+
                Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()
            )
            total_repairs_by_motifs += total_repairs_by_motif
            total_motif_arrets += total_motif_arret 
            
            all_rep_visit = Reparation.objects.filter(vehicule=vehicule, motif="Visite", date_saisie__month=month, date_saisie__year=year).count()
            all_rep_panne = Reparation.objects.filter(vehicule=vehicule, motif="Panne", date_saisie__month=month, date_saisie__year=year).count()
            all_rep_accident = Reparation.objects.filter(vehicule=vehicule, motif="Accident", date_saisie__month=month, date_saisie__year=year).count()
            all_autre_arret = Autrarret.objects.filter(vehicule=vehicule, date_saisie__month=month, date_saisie__year=year).count()
            
            vehicule_data.append({
                'immatriculation': vehicule.immatriculation,
                'marque': vehicule.marque,
                'total_actions': total_actions,
                'total_cost_parts': total_cost_parts,
                'total_income': total_income,
                'part_details': part_details,
                'daily_actions': daily_actions,
                'repairs_by_motif': repairs_by_motif,
                'motif_arret': motif_arret,
            })
            total_actions_sum += total_actions
            total_cost_parts_sum += total_cost_parts
            total_income_sum += total_income
            total_piece_sum += all_piece
    
            total_visitechique_sum += all_visitechnique
            total_entretien_sum += all_entretien
    
            total_visit_sum += all_rep_visit
            total_panne_sum += all_rep_panne
            total_accident_sum += all_rep_accident
            total_autrarret_sum += all_autre_arret
    
        context['vehicule_data'] = vehicule_data
        
        context['total_repairs_by_motifs'] = total_repairs_by_motifs
        context['total_motif_arrets'] = total_motif_arrets
        
        context['total_visit_sum'] = total_visit_sum
        context['total_panne_sum'] = total_panne_sum
        context['total_accident_sum'] = total_accident_sum
        context['total_autrarret_sum'] = total_autrarret_sum
        
        context['total_visitechique_sum'] = total_visitechique_sum
        context['total_entretien_sum'] = total_entretien_sum
        
        context['total_actions_sum'] = total_actions_sum
        context['total_cost_parts_sum'] = total_cost_parts_sum
        context['total_income_sum'] = total_income_sum
        context['total_piece_sum'] = total_piece_sum
        
        context['days_in_month'] = range(1, days_in_month + 1)
        context['month_name'] = month_name
        context['month'] = month
        context['year'] = year
        context['years'] = range(timezone.now().year - 4, timezone.now().year + 1)
        context['month_range'] = range(1, 13)
        context['days_in_month_plus_two'] = days_in_month + 2
        return context

class SuiviFinancierView(TemplateView):
    model = Vehicule
    template_name = 'news/applist/suivie_financier_vehi.html' 
    context_object_name = 'vehicule'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        user_group = self.request.user.groups.first() 
        context['user_group'] = user_group.name if user_group else None 
        all_vehicule = Vehicule.objects.all() 
        resultat_vehicule = [] 
        form = DateForm(self.request.GET) 
        if form.is_valid(): 
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            if all_vehicule: 
                for vehicule in all_vehicule: 
                    recettes = Recette.objects.filter(date__range=[date_debut, date_fin],vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 1
                    charge_fix = ChargeFixe.objects.filter(date__range=[date_debut, date_fin],vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 0
                    charge_var = ChargeVariable.objects.filter(date__range=[date_debut, date_fin],vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 0
                    
                    Total_charge = charge_fix + charge_var
                    marg_contr = recettes - charge_var
                    taux_marge = (marg_contr*100/(recettes))
                    taux_marge_format ='{:.2f}'.format(taux_marge)
                    resultat = recettes-Total_charge
                    reparations = Reparation.objects.filter(date_entree__range=[date_debut, date_fin],vehicule = vehicule)
                    context['som_piece'] = Piece.objects.filter(date_achat__range=[date_debut, date_fin],reparation__in = reparations).aggregate(total_piece=Sum('cout'))['total_piece'] or 0
                    resultat_vehicule.append({'vehicule': vehicule, 'recettes':recettes, 'charge_fix':charge_fix, 'charge_var':charge_var, 'Total_charge':Total_charge, 'marg_contr':marg_contr, 'taux_marge_format':taux_marge_format, 'resultat': resultat, 'som_piece':context['som_piece'] or 0 })
            else:
                charge_fix =0
                charge_var =0
                Total_charge = 0
                marg_contr = 0
                taux_marge_format = 0
                resultat = 0
                marg_contr = 0
                resultat_vehicule = 0
                recettes = 0
        else:
            if all_vehicule:
                for vehicule in all_vehicule:
                    recettes = Recette.objects.filter(vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 1
                    charge_fix = ChargeFixe.objects.filter(vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 0
                    charge_var = ChargeVariable.objects.filter(vehicule = vehicule).aggregate(Sum('montant'))['montant__sum'] or 0

                    Total_charge = charge_fix + charge_var
                    marg_contr = recettes - charge_var
                    taux_marge = (marg_contr*100/(recettes))
                    taux_marge_format ='{:.2f}'.format(taux_marge)
                    resultat = recettes-Total_charge
                    reparations = Reparation.objects.filter(vehicule = vehicule)
                    context['som_piece'] = Piece.objects.filter(reparation__in = reparations).aggregate(total_piece=Sum('cout'))['total_piece'] or 0
                    resultat_vehicule.append({'vehicule': vehicule, 'recettes':recettes, 'charge_fix':charge_fix, 'charge_var':charge_var, 'Total_charge':Total_charge, 'marg_contr':marg_contr, 'taux_marge_format':taux_marge_format, 'resultat': resultat, 'som_piece':context['som_piece'] or 0 })
            else:
                charge_fix =0
                charge_var =0
                Total_charge = 0
                marg_contr = 0
                taux_marge_format = 0
                resultat = 0
                marg_contr = 0
                resultat_vehicule = 0
                recettes = 0
        #context['som_piece'] = som_piece 
        context['catego_vehi'] = CategoVehi.objects.all()
        context['charge_fix'] = charge_fix
        context['charge_var'] = charge_var
        context['Total_charge'] = Total_charge
        context['marg_contr'] = marg_contr
        context['taux_marge_format'] = taux_marge_format
        context['resultat'] = resultat
        context['resultat_vehicule'] = resultat_vehicule
        context['all_vehicule'] = all_vehicule
        context['total_recet_verse'] = recettes
        context['form'] = form
        return context

class MyRecetteView(CustomPermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = "perfect/myrecette.html"
    permission_url = 'rec_day'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenir la date actuelle
        today = now().date()
        month = self.request.GET.get('month', today.month)
        year = self.request.GET.get('year', today.year)
        month = int(month)
        year = int(year)
        days_in_month = monthrange(year, month)[1]
        month_name = datetime(year, month, 1).strftime("%B")
        # Calculer les dimanches dans le mois
        dimanches = [
            day for day in range(1, days_in_month + 1)
            if datetime(year, month, day).weekday() == SUNDAY
        ]
        jours_ouvrables = days_in_month - len(dimanches)
        # Initialisation des variables
        vehicules = Vehicule.objects.select_related('category').all()
        recette_details = []
        # Totaux cumulés
        total_recette_mensuelle = 0
        total_recette_annuelle = 0
        sum_recets_jours = 0
        sum_difference_mensuelle = 0
        sum_recettes_vehicule_mois = 0
        sum_difference = 0
        sum_motif_arrets = 0
        
        for vehicule in vehicules:
            # Recette journalière
            recettes_vehicule_jour = Recette.objects.filter(
                vehicule=vehicule,
                date_saisie=date.today()
            ).aggregate(total_recette=Sum('montant'))['total_recette'] or 0
            # Recette mensuelle
            recettes_vehicule_mois = Recette.objects.filter(
                vehicule=vehicule,
                date_saisie__month=month,
                date_saisie__year=year
            ).aggregate(total_recette=Sum('montant'))['total_recette'] or 0
            # Recette annuelle
            recettes_vehicule_an = Recette.objects.filter(
                vehicule=vehicule,
                date_saisie__year=year
            ).aggregate(total_recette=Sum('montant'))['total_recette'] or 0
            # Recette par défaut de la catégorie
            recette_defaut = vehicule.category.recette_defaut
            # Calcul de la recette mensuelle attendue sans dimanches
            recette_attendue_mensuelle = recette_defaut * jours_ouvrables
            # Calcul de la différence pour aujourd'hui
            difference = recettes_vehicule_jour - recette_defaut
            difference_mensuelle = recettes_vehicule_mois - recette_attendue_mensuelle
            sum_difference_mensuelle += difference_mensuelle
            sum_recettes_vehicule_mois += recettes_vehicule_mois
            sum_difference += difference
            
            motif_arrets = {
                'vis': VisiteTechnique.objects.filter(vehicule=vehicule,date_saisie=date.today()).count(),
                'ent': Entretien.objects.filter(vehicule=vehicule, date_saisie=date.today()).count(),
                'rep': Reparation.objects.filter(vehicule=vehicule, date_saisie=date.today()).count(),
            }
            visite = VisiteTechnique.objects.filter(vehicule=vehicule,date_saisie=date.today()).count()
            entretien = Entretien.objects.filter(vehicule=vehicule, date_saisie=date.today()).count()
            reparation = Reparation.objects.filter(vehicule=vehicule, date_saisie=date.today()).count()
            som_des_motifs = visite+entretien+reparation
            
            sum_motif_arrets += som_des_motifs
            sum_recets_jours += recettes_vehicule_jour
            daily_actions = [0] * days_in_month
            for day in range(1, days_in_month + 1):
                for model in [Recette]:
                    motant = model.objects.filter(
                        vehicule=vehicule, date_saisie__day=day, date_saisie__month=month, date_saisie__year=year
                    ).aggregate(somme=Sum('montant'))['somme'] or 0
                    daily_actions[day - 1] += motant
            # Ajouter les détails journaliers au contexte
            recette_details.append({
                'vehicule': vehicule.immatriculation,
                'marque': vehicule.marque,
                'recette_versee': recettes_vehicule_jour,
                'recette_attendue': recette_defaut,
                'daily_actions': daily_actions,
                'difference': difference,
                'difference_mensuelle': difference_mensuelle,
                'recette_mensuelle': recettes_vehicule_mois,
                'recette_annuelle': recettes_vehicule_an,
                'motif_arrets': motif_arrets,
            })
            
        catevtc = CategoVehi.objects.filter(category='VTC').first()
        catetaxi = CategoVehi.objects.filter(category='TAXI').first()
        recette_vtc_attendue = catevtc.recette_defaut * jours_ouvrables if catevtc else 0
        recette_taxi_attendue = catetaxi.recette_defaut * jours_ouvrables if catetaxi else 0
        
        context['sum_motif_arrets'] = sum_motif_arrets
        context['sum_difference'] = sum_difference
        context['sum_recettes_vehicule_mois'] = sum_recettes_vehicule_mois
        context['sum_difference_mensuelle'] = sum_difference_mensuelle
        context['sum_recets_jours'] = sum_recets_jours
        context['recette_details'] = recette_details
        context['recette_vtc_attendue'] = recette_vtc_attendue
        context['recette_taxi_attendue'] = recette_taxi_attendue
        context['total_recette_mensuelle'] = total_recette_mensuelle
        context['total_recette_annuelle'] = total_recette_annuelle
        context['current_date'] = today
        context['days_in_month'] = range(1, days_in_month + 1)
        context['month_name'] = month_name
        context['month'] = month
        context['year'] = year
        context['years'] = range(today.year - 4, today.year + 1)
        context['month_range'] = range(1, 13)
        context['days_in_month_plus_two'] = days_in_month + 2
        return context
    
class DashboardView(CustomPermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    login_url = 'login'
    permission_url = 'dash'
    template_name = 'perfect/dashboard.html'
    form_class = DateForm
    timeout_minutes = 600
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get(self, request, *args, **kwargs):
        request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().post(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        vehicules = Vehicule.objects.all()

        form = self.form_class(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            
            catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
            ################################----Recettes----#############################
            total_recettes = Recette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
            
            total_recettes_vtc = Recette.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_vtc_format ='{:,}'.format(total_recettes_vtc).replace('',' ')
            
            total_recettes_taxi = Recette.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_taxi_format ='{:,}'.format(total_recettes_taxi).replace('',' ')
            
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
            total_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            total_charge_format ='{:,}'.format(total_charg).replace('',' ')
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
            
            ################################----Graphiques----#############################
            recet_data_vtc = Recette.objects.filter(vehicule__category__category ='VTC', date_saisie__range=[date_debut, date_fin])
            recet_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data_vtc:
                recet_mois_vtc_data[commande.date_saisie.month] += commande.montant
            recet_mois_vtc_data = [recet_mois_vtc_data[month] for month in range(1, 13)]
            
            recet_data_taxi = Recette.objects.filter(vehicule__category__category ='TAXI', date_saisie__range=[date_debut, date_fin])
            recet_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data_taxi:
                recet_mois_taxi_data[commande.date_saisie.month] += commande.montant
            recet_mois_taxi_data = [recet_mois_taxi_data[month] for month in range(1, 13)]
            
            rep_vtc_data = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in rep_vtc_data:
                rep_mois_vtc_data[commande.date_saisie.month] += 1
            rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
            
            rep_taxi_data = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            rep_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in rep_taxi_data:
                rep_mois_taxi_data[commande.date_saisie.month] += 1
            rep_mois_taxi_data = [rep_mois_taxi_data[month] for month in range(1, 13)]
            
            piec_vtc_data = Piece.objects.filter(reparation__in=rep_vtc_data,date_saisie__range=[date_debut, date_fin])
            piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piec_vtc_data:
                piec_mois_vtc_data[commande.date_saisie.month] += 1
            piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
            piec_taxi_data = Piece.objects.filter(reparation__in=rep_taxi_data,date_saisie__range=[date_debut, date_fin])
            piec_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piec_taxi_data:
                piec_mois_taxi_data[commande.date_saisie.month] += 1
            piec_mois_taxi_data = [piec_mois_taxi_data[month] for month in range(1, 13)]
            
            piecha_vtc_data = PiecEchange.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_vtc_data:
                piecha_mois_vtc_data[commande.date_saisie.month] += 1
            piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
            piecha_taxi_data = PiecEchange.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            piecha_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_taxi_data:
                piecha_mois_taxi_data[commande.date_saisie.month] += 1
            piecha_mois_taxi_data = [piecha_mois_taxi_data[month] for month in range(1, 13)]
            
            chargfix_vtc_data = ChargeFixe.objects.filter(vehicule__category__category ='VTC', date_saisie__range=[date_debut, date_fin])
            chargfix_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_vtc_data:
                chargfix_mois_vtc_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_vtc_data = [chargfix_mois_vtc_data[month] for month in range(1, 13)]
            
            chargfix_taxi_data = ChargeFixe.objects.filter(vehicule__category__category ='TAXI', date_saisie__range=[date_debut, date_fin])
            chargfix_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_taxi_data:
                chargfix_mois_taxi_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_taxi_data = [chargfix_mois_taxi_data[month] for month in range(1, 13)]
            ###########################################################################################################################################################
            chargvar_vtc_data = ChargeVariable.objects.filter(vehicule__category__category ='VTC',date_saisie__range=[date_debut, date_fin])
            chargvar_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_vtc_data:
                chargvar_mois_vtc_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_vtc_data = [chargvar_mois_vtc_data[month] for month in range(1, 13)]
            
            chargvar_taxi_data = ChargeVariable.objects.filter(vehicule__category__category ='TAXI',date_saisie__range=[date_debut, date_fin])
            chargvar_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_taxi_data:
                chargvar_mois_taxi_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_taxi_data = [chargvar_mois_taxi_data[month] for month in range(1, 13)]
            
            chargvar_data = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin])
            chargvar_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_data:
                chargvar_mois_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
            ###########################################################################################################################################################
            recet_taux_data = {month: 0 for month in range(1, 13)}
            chargvar_taux_data = {month: 0 for month in range(1, 13)}
            marge_data_vtc = [recet_mois_vtc_data[i] - chargvar_mois_data[i] for i in range(12)]
            taux_data_vtc = [(marge_data_vtc[i] * 100) / recet_mois_vtc_data[i] if recet_mois_vtc_data[i] > 0 else 0 for i in range(12)]
            
            ################################TAXI################################
            marge_data_taxi = [recet_mois_taxi_data[i] - chargvar_mois_data[i] for i in range(12)]
            # Calcul des taux mensuels
            taux_data_taxi = [(marge_data_taxi[i] * 100) / recet_mois_taxi_data[i] if recet_mois_taxi_data[i] > 0 else 0 for i in range(12)]
            #########################################---Meilleur---####################################
            marge_contri = []
            all_vehicule = Vehicule.objects.all()[:6]
            all_recettes = Recette.objects.all()[:6]
            best_recets = []
            best_marge = []
            best_taux = []
            for vehicule in all_vehicule:
                recs = Recette.objects.filter(vehicule=vehicule,date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
                rece_all = recs if recs is not None else 0
                charges_variables = ChargeVariable.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
                chargvari_all = charges_variables if charges_variables is not None else 0
                marge_cont = rece_all - chargvari_all
                marge = marge_cont if marge_cont is not None else 0
                if rece_all == 0:
                    taux=0
                else:
                    taux = round((marge*100)/rece_all,2)
                    taux = taux if taux is not None else 0
                    
                best_taux.append({'vehicule': vehicule, 'taux':taux})
                best_marge.append({'vehicule': vehicule, 'marge_cont':marge_cont})
                best_recets.append({'vehicule': vehicule, 'recs':recs})
            best_marge = sorted([x for x in best_marge if x['marge_cont'] is not None], key=lambda x: x['marge_cont'], reverse=True)[:5] 
            best_taux = sorted(best_taux, key=lambda x: x['taux'], reverse=True)[:5]  
            best_recets = sorted([x for x in best_recets if x['recs'] is not None], key=lambda x: x['recs'], reverse=True)[:5]
            
        else:
            catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
            ################################----Recettes----#############################
            total_recettes = Recette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
            
            total_recettes_vtc = Recette.objects.filter(vehicule__category__category="VTC",date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_vtc_format ='{:,}'.format(total_recettes_vtc).replace('',' ')
            total_recettes_taxi = Recette.objects.filter(vehicule__category__category="TAXI",date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_taxi_format ='{:,}'.format(total_recettes_taxi).replace('',' ')
            
            ################################----Pieces----#############################
            total_piece= Piece.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            ################################-----#----Pieces echanges----#-----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
            total_charg_var = ChargeVariable.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            total_charge_format ='{:,}'.format(total_charg).replace('',' ')
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            ################################----Taux----#############################
            if total_recettes == 1:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
            
            ################################----Graphiques----#############################
            recet_data_vtc = Recette.objects.filter(vehicule__category__category="VTC", date_saisie__year=datetime.now().year)
            recet_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data_vtc:
                recet_mois_vtc_data[commande.date_saisie.month] += commande.montant
            recet_mois_vtc_data = [recet_mois_vtc_data[month] for month in range(1, 13)]
            
            recet_data_taxi = Recette.objects.filter(vehicule__category__category = 'TAXI', date_saisie__year=datetime.now().year)
            recet_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data_taxi:
                recet_mois_taxi_data[commande.date_saisie.month] += commande.montant
            recet_mois_taxi_data = [recet_mois_taxi_data[month] for month in range(1, 13)]
            
            rep_vtc_data = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in rep_vtc_data:
                rep_mois_vtc_data[commande.date_saisie.month] += 1
            rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
            rep_taxi_data = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            rep_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in rep_taxi_data:
                rep_mois_taxi_data[commande.date_saisie.month] += 1
            rep_mois_taxi_data = [rep_mois_taxi_data[month] for month in range(1, 13)]
            
            piec_vtc_data = Piece.objects.filter(reparation__in=rep_vtc_data,date_saisie__year=datetime.now().year)
            piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piec_vtc_data:
                piec_mois_vtc_data[commande.date_saisie.month] += 1
            piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
            piec_taxi_data = Piece.objects.filter(reparation__in=rep_taxi_data,date_saisie__year=datetime.now().year)
            piec_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piec_taxi_data:
                piec_mois_taxi_data[commande.date_saisie.month] += 1
            piec_mois_taxi_data = [piec_mois_taxi_data[month] for month in range(1, 13)]
            
            piecha_vtc_data = PiecEchange.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_vtc_data:
                piecha_mois_vtc_data[commande.date_saisie.month] += 1
            piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
            piecha_taxi_data = PiecEchange.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            piecha_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_taxi_data:
                piecha_mois_taxi_data[commande.date_saisie.month] += 1
            piecha_mois_taxi_data = [piecha_mois_taxi_data[month] for month in range(1, 13)]
            
            chargvar_data = ChargeVariable.objects.filter(date_saisie__year=datetime.now().year)
            chargvar_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_data:
                chargvar_mois_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
            
            ###########################################################################################################################################################
            
            chargfix_vtc_data = ChargeFixe.objects.filter(vehicule__category__category ='VTC', date_saisie__year=datetime.now().year)
            chargfix_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_vtc_data:
                chargfix_mois_vtc_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_vtc_data = [chargfix_mois_vtc_data[month] for month in range(1, 13)]
            
            chargfix_taxi_data = ChargeFixe.objects.filter(vehicule__category__category ='TAXI', date_saisie__year=datetime.now().year)
            chargfix_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_taxi_data:
                chargfix_mois_taxi_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_taxi_data = [chargfix_mois_taxi_data[month] for month in range(1, 13)]
            ###########################################################################################################################################################
            chargvar_vtc_data = ChargeVariable.objects.filter(vehicule__category__category ='VTC',date_saisie__year=datetime.now().year)
            chargvar_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_vtc_data:
                chargvar_mois_vtc_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_vtc_data = [chargvar_mois_vtc_data[month] for month in range(1, 13)]
            
            chargvar_taxi_data = ChargeVariable.objects.filter(vehicule__category__category ='TAXI',date_saisie__year=datetime.now().year)
            chargvar_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_taxi_data:
                chargvar_mois_taxi_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_taxi_data = [chargvar_mois_taxi_data[month] for month in range(1, 13)]
            ###########################################################################################################################################################
            
            recet_taux_data = {month: 0 for month in range(1, 13)}
            chargvar_taux_data = {month: 0 for month in range(1, 13)}
            
            ################################VTC################################
            marge_data_vtc = [recet_mois_vtc_data[i] - chargvar_mois_data[i] for i in range(12)]
            taux_data_vtc = [(marge_data_vtc[i] * 100) / recet_mois_vtc_data[i] if recet_mois_vtc_data[i] > 0 else 0 for i in range(12)]
            
            ################################TAXI################################
            marge_data_taxi = [recet_mois_taxi_data[i] - chargvar_mois_data[i] for i in range(12)]
            # Calcul des taux mensuels
            taux_data_taxi = [(marge_data_taxi[i] * 100) / recet_mois_taxi_data[i] if recet_mois_taxi_data[i] > 0 else 0 for i in range(12)]
            #########################################---Meilleur---####################################
            marge_contri = []
            all_vehicule = Vehicule.objects.all()[:6]
            all_recettes = Recette.objects.all()[:6]
            best_recets = []
            best_marge = []
            best_taux = []
            for vehicule in all_vehicule:
                recs = Recette.objects.filter(vehicule=vehicule,date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
                rece_all = recs if recs is not None else 0
                charges_variables = ChargeVariable.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
                chargvari_all = charges_variables if charges_variables is not None else 0
                marge_cont = rece_all - chargvari_all
                marge = marge_cont if marge_cont is not None else 0
                if rece_all == 0:
                    taux=0
                else:
                    taux = round((marge*100)/rece_all,2)
                    taux = taux if taux is not None else 0
                best_taux.append({'vehicule': vehicule, 'taux':taux})
                best_marge.append({'vehicule': vehicule, 'marge_cont':marge_cont})
                best_recets.append({'vehicule': vehicule, 'recs':recs})
            best_marge = sorted([x for x in best_marge if x['marge_cont'] is not None], key=lambda x: x['marge_cont'], reverse=True)[:5] 
            best_taux = sorted(best_taux, key=lambda x: x['taux'], reverse=True)[:5]  
            best_recets = sorted([x for x in best_recets if x['recs'] is not None], key=lambda x: x['recs'], reverse=True)[:5]

        context={
            'tot_recets':total_recette_format,
            'total_recette_taxi_format':total_recette_taxi_format,
            'total_recette_vtc_format':total_recette_vtc_format,
            
            'vehicules':vehicules,
            'tot_piece':total_piece_format,
            'tot_piec_echang':total_piece_echang_format,
            'tot_chargfix':total_chargfix_format,
            'tot_chargvar':total_chargvar_format,
            'charge_totale':total_charge_format,
            'marge_brute_format':marge_brute_format,
            'taux_marge':taux_marge_format,
            'best_recettes':best_recets,
            'bests_taux':best_taux,
            'mois':libelle_mois_en_cours,
            
            #################---###############-----Graphiq-----#################---###############
            'recet_mois_vtc_data':recet_mois_vtc_data,
            'recet_mois_taxi_data':recet_mois_taxi_data,
            
            'chargevar_data':chargvar_mois_data,
            
            'taux_data_vtc':taux_data_vtc,
            'taux_data_taxi':taux_data_taxi,
            
            'chargvar_mois_taxi_data':chargvar_mois_taxi_data,
            'chargvar_mois_vtc_data':chargvar_mois_vtc_data,
            
            'chargfix_mois_taxi_data':chargfix_mois_taxi_data,
            'chargfix_mois_vtc_data':chargfix_mois_vtc_data,
            
            'piecha_mois_vtc_data':piecha_mois_vtc_data,
            'piec_mois_vtc_data':piec_mois_vtc_data,
            'piecha_mois_taxi_data':piecha_mois_taxi_data,
            'piec_mois_taxi_data':piec_mois_taxi_data,
            
            'labels':label,
            'form':form,
            'dates':dates,
            # 'permissions':permissions
        }
        return context
    






























class DashboardMView(TemplateView):
    # login_url = 'login'
    # permission_url = 'dash'
    template_name = 'perfect/dashboardmjr.html'
    form_class = DateFormMJR
    timeout_minutes = 600
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get(self, request, *args, **kwargs):
        request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().post(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        marge_cont = []
        best_recets = []
        best_marge = []
        best_taux = []
        labelscat = []
        datacat = []
        datasets = []
        jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        recet_taux_data = {month: 0 for month in range(1, 13)}
        chargvar_taux_data = {month: 0 for month in range(1, 13)}
        categories = CategoVehi.objects.all()
        count_catego = categories.count()
        vehicules = Vehicule.objects.all()

        recette_queryset = Recette.objects.all()
        chargfix_queryset = ChargeFixe.objects.all()
        chargvar_queryset = ChargeVariable.objects.all()
        reparation_queryset = Reparation.objects.all()
        piechan_queryset = PiecEchange.objects.all()
        piece_queryset = Piece.objects.all()

        all_vehicule = vehicules[:6]
        all_recettes = recette_queryset[:6]
        form = self.form_class(self.request.GET)
        
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            
        if categorie_filter:
            recette_queryset = recette_queryset.filter(vehicule__category__category=categorie_filter)
            chargfix_queryset = chargfix_queryset.filter(vehicule__category__category=categorie_filter)
            chargvar_queryset = chargvar_queryset.filter(vehicule__category__category=categorie_filter)
            reparation_queryset = reparation_queryset.filter(vehicule__category__category=categorie_filter)
            piechan_queryset = piechan_queryset.filter(vehicule__category__category=categorie_filter)
            piece_queryset = piece_queryset.filter(reparation__vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            recette_queryset = recette_queryset.filter(date_saisie__range=[date_debut, date_fin])
            chargfix_queryset = chargfix_queryset.filter(date_saisie__range=[date_debut, date_fin])
            chargvar_queryset = chargvar_queryset.filter(date_saisie__range=[date_debut, date_fin])
            reparation_queryset = reparation_queryset.filter(date_saisie__range=[date_debut, date_fin])
            piechan_queryset = piechan_queryset.filter(date_saisie__range=[date_debut, date_fin])
            piece_queryset = piece_queryset.filter(date_saisie__range=[date_debut, date_fin])

        # catego_vehi = CategoVehi.objects.all().annotate(vehicule_count=Count("category"))
        # ################################----Recettes----#############################
        total_recettes = recette_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
        # ################################----Pieces----#############################
        total_piece=piece_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
        total_piece_format ='{:,}'.format(total_piece).replace('',' ')
        # ################################-----#----Pieces echanges----#-----#############################
        total_piec_echange= piechan_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
        total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
        # ################################----Charges----#############################
        total_charg_fix = chargfix_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
        total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
        total_charg_var = chargvar_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
        total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
        # ################################----Charge Totale----#############################
        total_charg = total_charg_fix + total_charg_var
        total_charge_format ='{:,}'.format(total_charg).replace('',' ')
        ################################----Marge de contribution----#############################
        marge_contribution = total_recettes - total_charg
        marge_contribution = total_recettes - total_charg_var
        # ################################----Taux----#############################
        if total_recettes == 1:
            taux_marge = 0
        else:
            taux_marge = (marge_contribution*100/(total_recettes))
        taux_marge_format ='{:.2f}'.format(taux_marge)
        
        # ################################----Marge brute----#############################
        marge_brute = total_recettes - total_charg
        marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
        
        # ################################----Graphiques----#############################
        recet_data_vtc = recette_queryset.filter(date_saisie__year=datetime.now().year)
        recet_mois_vtc_data = {month: 0 for month in range(1, 13)}
        for commande in recet_data_vtc:
            recet_mois_vtc_data[commande.date_saisie.month] += commande.montant
        recet_mois_vtc_data = [recet_mois_vtc_data[month] for month in range(1, 13)]
        
        rep_vtc_data = reparation_queryset.filter(date_saisie__year=datetime.now().year)
        rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
        for commande in rep_vtc_data:
            rep_mois_vtc_data[commande.date_saisie.month] += 1
        rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
        
        piec_vtc_data = piece_queryset.filter(reparation__in=rep_vtc_data, date_saisie__year=datetime.now().year)
        piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
        for commande in piec_vtc_data:
            piec_mois_vtc_data[commande.date_saisie.month] += 1
        piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
        
        piecha_vtc_data = piechan_queryset.filter(date_saisie__year=datetime.now().year)
        piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
        for commande in piecha_vtc_data:
            piecha_mois_vtc_data[commande.date_saisie.month] += 1
        piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
        
        chargvar_data = chargvar_queryset.filter(date_saisie__year=datetime.now().year)
        chargvar_mois_data = {month: 0 for month in range(1, 13)}
        for commande in chargvar_data:
            chargvar_mois_data[commande.date_saisie.month] += commande.montant
        chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
        
        # ###########################################################################################################################################################
        
        chargfix_vtc_data = chargfix_queryset.filter(date_saisie__year=datetime.now().year)
        chargfix_mois_vtc_data = {month: 0 for month in range(1, 13)}
        for commande in chargfix_vtc_data:
            chargfix_mois_vtc_data[commande.date_saisie.month] += commande.montant
        chargfix_mois_vtc_data = [chargfix_mois_vtc_data[month] for month in range(1, 13)]
        
        # ###########################################################################################################################################################
        chargvar_vtc_data = chargvar_queryset.filter(date_saisie__year=datetime.now().year)
        chargvar_mois_vtc_data = {month: 0 for month in range(1, 13)}
        for commande in chargvar_vtc_data:
            chargvar_mois_vtc_data[commande.date_saisie.month] += commande.montant
        chargvar_mois_vtc_data = [chargvar_mois_vtc_data[month] for month in range(1, 13)]
        
        # ################################VTC################################
        marge_data_vtc = [recet_mois_vtc_data[i] - chargvar_mois_data[i] for i in range(12)]
        taux_data_vtc = [(marge_data_vtc[i] * 100) / recet_mois_vtc_data[i] if recet_mois_vtc_data[i] > 0 else 0 for i in range(12)]
        
        for vehicule in all_vehicule:
            recs = recette_queryset.filter(vehicule=vehicule,date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            rece_all = recs if recs is not None else 0
            charges_variables = chargvar_queryset.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            chargvari_all = charges_variables if charges_variables is not None else 0
            marge_cont = rece_all - chargvari_all
            marge = marge_cont if marge_cont is not None else 0
            if rece_all == 0:
                taux=0
            else:
                taux = round((marge*100)/rece_all,2)
                taux = taux if taux is not None else 0
            best_taux.append({'vehicule': vehicule, 'taux':taux})
            best_marge.append({'vehicule': vehicule, 'marge_cont':marge_cont})
            best_recets.append({'vehicule': vehicule, 'recs':recs})
        best_marge = sorted([x for x in best_marge if x['marge_cont'] is not None], key=lambda x: x['marge_cont'], reverse=True)[:5] 
        best_taux = sorted(best_taux, key=lambda x: x['taux'], reverse=True)[:5]  
        best_recets = sorted([x for x in best_recets if x['recs'] is not None], key=lambda x: x['recs'], reverse=True)[:5]


        rectte_par_categorie = recette_queryset.values(
            'vehicule__category__category'
        ).annotate(
            total=Sum('montant')
        ).order_by('-total')
        # Extraire les données pour le graphique
        labelscat = [item['vehicule__category__category'] for item in rectte_par_categorie]
        datacat = [item['total'] for item in rectte_par_categorie]

        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())  # Lundi
        end_of_week = start_of_week + timedelta(days=5)
        
        for categorie in categories:
            ventes = [0] * 6
            lignes = (
                recette_queryset.filter(
                    vehicule__category__category=categorie,
                    date_saisie__range=[start_of_week, end_of_week]
                ).annotate(
                    jour=F("date_saisie"),
                    total=Sum("montant")
                ).values("jour", "total").order_by('-total')
            )
            for ligne in lignes:
                day_index = ligne["jour"].weekday()
                if day_index < 6:
                    ventes[day_index] = float(ligne["total"]) if ligne["total"] else 0

            datasets.append({
                "label": categorie.category.upper(),
                "data": ventes,
                "fill": True,
            })

        context={
            'total_recette_format':total_recette_format,
            "datasets_json": json.dumps(datasets),
            "jours_semaine" : jours_semaine,
            
            'vehicules':vehicules,
            'tot_piece':total_piece_format,
            'tot_piec_echang':total_piece_echang_format,
            'tot_chargfix':total_chargfix_format,
            'tot_chargvar':total_chargvar_format,
            'charge_totale':total_charge_format,
            'marge_brute_format':marge_brute_format,
            'taux_marge':taux_marge_format,
            'best_recettes':best_recets,
            'bests_taux':best_taux,
            'mois':libelle_mois_en_cours,
            
            #################---###############-----Graphiq-----#################---###############
            'recet_mois_vtc_data':recet_mois_vtc_data,
            
            'chargevar_data':chargvar_mois_data,
            
            'taux_data_vtc':taux_data_vtc,
            
            'chargvar_mois_vtc_data':chargvar_mois_vtc_data,
            
            'chargfix_mois_vtc_data':chargfix_mois_vtc_data,
            
            'piecha_mois_vtc_data':piecha_mois_vtc_data,
            'piec_mois_vtc_data':piec_mois_vtc_data,
            'labels':label,
            'form':form,
            'dates':dates,

            'labelscat':labelscat,
            'datacat':datacat,
            # 'permissions':permissions
        }
        return context
    
class BilletageView(CustomPermissionRequiredMixin, CreateView):
    model = Billetage
    permission_url = 'billetage'
    form_class = BilletageForm
    template_name = 'perfect/caisse.html'
    success_message = 'Saisie enrégistrée avec succès✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('billetage')
    timeout_minutes = 230
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        form = self.get_form()
        forms = DatebilanForm(self.request.GET)
        if forms.is_valid():
            date_bilan = forms.cleaned_data['date_bilan']
            encaisser = Encaissement.objects.filter(date_saisie=date_bilan)
            decaisser = Decaissement.objects.filter(date_saisie=date_bilan)
            solde_jour = SoldeJour.objects.filter(date_saisie=date_bilan).aggregate(Sum('montant'))['montant__sum'] or 0
            # Calculer le total des encaissements pour la journée actuelle
            tot_entree = Encaissement.objects.filter(date_saisie=date_bilan).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sortie = Decaissement.objects.filter(date_saisie=date_bilan).aggregate(somme=Sum('montant'))['somme'] or 0
            
            solde_initial = None
            # Vérifier le solde des 3 derniers jours, en commençant par hier
            for i in range(1, 4):
                solde_temp = SoldeJour.objects.filter(date_saisie=date_bilan - timedelta(days=i)).first()
                if solde_temp:
                    solde_initial = solde_temp.montant
                    break
                
            # Si aucun solde trouvé dans les 3 derniers jours, utiliser le premier solde initial enregistré
            if not solde_initial:
                solde_initial_record = SoldeJour.objects.filter(date_saisie=date_bilan - timedelta(days=1)).first()
                solde_initial = solde_initial_record.montant if solde_initial_record else 0
                
            som_entree = tot_entree + solde_initial
            solde_fin_journee = som_entree - tot_sortie
            
            som_billets = Billetage.objects.filter(type='Billet', date_saisie=date_bilan).aggregate(somme=Sum('valeur'))['somme'] or 0
            
            som_pieces = Billetage.objects.filter(type='Pièce', date_saisie=date_bilan).aggregate(somme=Sum('valeur'))['somme'] or 0
            som_billets = som_billets
            som_pieces = som_pieces

            bill = Billetage.objects.filter(type='Billet', date_saisie=date_bilan)
            bil = []
            som_tot_bil = 0
            for b in bill:
                val = b.valeur
                nb = b.nombre
                res = b.valeur * b.nombre
                som_tot_bil += res or 0
                bil.append({'val': val, 'nb':nb,'res':res})
            som_tot_bil = som_tot_bil
            bil = bil

            piece = Billetage.objects.filter(type='Pièce', date_saisie=date_bilan)
            pie = []
            som_tot_piec = 0
            for p in piece:
                val = p.valeur or 0
                nb = p.nombre or 0
                res = p.valeur * p.nombre
                som_tot_piec += res or 0
                pie.append({'val': val, 'nb':nb,'res':res})
            som_tot_piec = som_tot_piec
            pie = pie
            
            Total_piec_bill = som_tot_piec + som_tot_bil
            ecart = solde_fin_journee - Total_piec_bill
            self.request.user.save()
            
        else:
            encaisser = Encaissement.objects.filter(date_saisie=date.today())
            decaisser = Decaissement.objects.filter(date_saisie=date.today())
            solde_jour = SoldeJour.objects.filter(date_saisie=date.today()).aggregate(Sum('montant'))['montant__sum'] or 0
            # Calculer le total des encaissements pour la journée actuelle
            tot_entree = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sortie = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
            solde_initial = None

            # Vérifier le solde des 3 derniers jours, en commençant par hier
            for i in range(1, 4):
                solde_temp = SoldeJour.objects.filter(date_saisie=date.today() - timedelta(days=i)).first()
                if solde_temp:
                    solde_initial = solde_temp.montant
                    break
            # Si aucun solde trouvé dans les 3 derniers jours, utiliser le premier solde initial enregistré
            if not solde_initial:
                solde_initial_record = SoldeJour.objects.filter(date_saisie=date.today() - timedelta(days=1)).first()
                solde_initial = solde_initial_record.montant if solde_initial_record else 0
            som_entree = tot_entree + solde_initial
            solde_fin_journee = som_entree - tot_sortie
            
            som_billets = Billetage.objects.filter(type='Billet', date_saisie=date.today()).aggregate(somme=Sum('valeur'))['somme'] or 0
            nb_bill = Billetage.objects.filter(type='Billet', date_saisie=date.today()).count() 

            som_pieces = Billetage.objects.filter(type='Pièce', date_saisie=date.today()).aggregate(somme=Sum('valeur'))['somme'] or 0
            som_billets = som_billets
            som_pieces = som_pieces

            bill = Billetage.objects.filter(type='Billet', date_saisie=date.today())
            bil = []
            som_tot_bil = 0
            for b in bill:
                val = b.valeur
                nb = b.nombre
                res = b.valeur * b.nombre
                som_tot_bil += res or 0
                bil.append({'val': val, 'nb':nb,'res':res})
            som_tot_bil = som_tot_bil
            bil = bil

            piece = Billetage.objects.filter(type='Pièce', date_saisie=date.today())
            pie = []
            som_tot_piec = 0
            for p in piece:
                val = p.valeur or 0
                nb = p.nombre or 0
                res = p.valeur * p.nombre
                som_tot_piec += res or 0
                pie.append({'val': val, 'nb':nb,'res':res})
            som_tot_piec = som_tot_piec
            pie = pie
            
            Total_piec_bill = som_tot_piec + som_tot_bil
            ecart = solde_fin_journee - Total_piec_bill

            self.request.user.save()
            
        context={
            'forms':forms,
            'solde_initial':solde_initial,
            
            'ent':encaisser,
            'sort':decaisser,
            'ecart':ecart,
            
            'piecs':pie,
            'biels':bil,
            
            'sompiecs':som_tot_piec,
            'sombiels':som_tot_bil ,
            
            'tot_ent':tot_entree,
            'tot_sor':tot_sortie,
            'form':form,
            
            'solde_day':solde_jour,
            'tot_bi_pi':Total_piec_bill,
            'dates':dates,
        }
        return context

class AddDecaissementView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_decaisse'
    model = Decaissement
    form_class = DecaissementForm
    template_name = 'perfect/sortie_caiss.html'
    success_message = 'Sortie de caisse enregistrée avec succès✓✓'
    error_message = "Erreur de saisie ✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        annee_en_cours =date.today().year
        today = date.today()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            sortie_liste = Decaissement.objects.filter(date_saisie__range=[date_debut, date_fin])  
            
            result_filtre = Decaissement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_jour = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_mois = Decaissement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_annuel = Decaissement.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
              
        else:
            sortie_liste = Decaissement.objects.filter(date_saisie=date.today())  
            result_filtre = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            
            tot_sort_jour = Decaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_mois =  Decaissement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_sort_annuel = Decaissement.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
        context = {
            'form': form,
            'forms': forms,
            'tot_sort_jours': tot_sort_jour,
            'tot_sort_mois': tot_sort_mois,
            'tot_sort_annuel': tot_sort_annuel,
            'sorties_liste': sortie_liste,
            'resuults_filtre': result_filtre,
            
            'dates': today,
            'mois': libelle_mois_en_cours,
            'mois': libelle_mois_en_cours,
            'annee': annee_en_cours,
        }
        return context
    def get_success_url(self):
        return reverse('add_decaisse')

def delete_sortie_caisse(request, pk):
    try:
        decaissements = get_object_or_404(Decaissement, id=pk)
        decaissements.delete()
        messages.success(request, f"la sortie de caisse de {decaissements.Num_piece} - {decaissements.libelle} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_decaisse')

class AddEncaissementView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'addencaisse'
    model = Encaissement
    form_class = EncaissementForm
    template_name = 'perfect/entre_caisse.html'
    success_message = 'Entrée de caisse enregistrée avec succès✓✓'
    error_message = "Erreur de saisie ✘✘"
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        annee_en_cours =date.today().year
        today =date.today()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            enter_liste = Encaissement.objects.filter(date_saisie__range=[date_debut, date_fin])  
            result_filtre = Encaissement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entre_jour = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entree_mois = Encaissement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entree_annuel = Encaissement.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
              
        else:
            enter_liste = Encaissement.objects.filter(date_saisie=date.today())  
            result_filtre = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entre_jour = Encaissement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entree_mois = Encaissement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            tot_entree_annuel = Encaissement.objects.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            
        context = {
            'form': form,
            'tot_entre_jours': tot_entre_jour,
            'tot_entre_mois': tot_entree_mois,
            'tot_entre_annuel': tot_entree_annuel,
            'enter_liste': enter_liste,
            'resuults_filtre': result_filtre,
            
            'dates': today,
            'mois': libelle_mois_en_cours,
            'mois': libelle_mois_en_cours,
            'annee': annee_en_cours,
            'forms': forms,
        }
        return context
    def get_success_url(self):
        return reverse('addencaisse')
    
def delete_entre_caisse(request, pk):
    try:
        encaissements = get_object_or_404(Encaissement, id=pk)
        encaissements.delete()
        messages.success(request, f"l'entrée de caisse de {encaissements.Num_piece} - {encaissements.libelle} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('addencaisse')

class AddSoldeJourView(CustomPermissionRequiredMixin, CreateView):
    permission_url = 'add_solde'
    model = SoldeJour
    form_class = Solde_JourForm
    template_name = 'perfect/solde.html'
    success_message = 'le solde de la journée a été enregistré avec succès✓✓'
    error_message = "Un solde existe deja pour cette journée ✘✘ "
    success_url = reverse_lazy ('add_solde')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        # Vérifie si un solde existe déjà pour la date spécifiée
        date = form.cleaned_data['date_saisie']
        form.instance.auteur = self.request.user
        messages.success(self.request, self.success_message)
        solde_exist = SoldeJour.objects.filter(date_saisie=date).exists()
        if solde_exist:
            # Si un solde existe déjà pour cette date, renvoie une erreur
            form.add_error('date', 'Un solde existe déjà pour cette date.')
            return self.form_invalid(form)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            solde_liste = SoldeJour.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            solde_liste = SoldeJour.objects.filter(date_saisie__month=date.today().month).order_by('-id')
        context = {
            'form': form,
            'soldes_liste': solde_liste,
            'forms': forms,
        }
        return context
 
def delete_solde(request, pk):
    try:
        solde = get_object_or_404(SoldeJour, id=pk)
        solde.delete()
        messages.success(request, f"le solde de la journee du {solde.date_saisie} - {solde.montant} frscfa a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_solde')
     
class GestionalerteView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):  
    permission_url = 'alerte'  
    login_url = 'login'                                                                      
    template_name = 'perfect/alerte.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def send_alert_email(self, vehicle_reference, alert_types):
        today_date = datetime.now().strftime("%Y-%m-%d")
        last_sent_alerts = self.request.session.get('last_sent_alerts', {})
        if last_sent_alerts.get(vehicle_reference) == today_date:
            return  
        alert_message = ", ".join(alert_types)
        subject = "Alerte : Maintenance du véhicule requise"
        message = (
            f"Le véhicule avec l'immatriculation {vehicle_reference} requiert une attention pour : {alert_message}. "
            "Veuillez vérifier les alertes associées."
        )
        recipient_list = ['sorothodaniel@gmail.com', 'atsinyapi1@gmail.com','konangerardk63@gmail.com','kougblaayaoviotodjo@gmail.com']
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        
        # Mettre à jour la session pour éviter un envoi multiple le même jour
        last_sent_alerts[vehicle_reference] = today_date
        self.request.session['last_sent_alerts'] = last_sent_alerts
        
    def get_context_data(self,*args, **kwargs):  
        context = super().get_context_data(*args,**kwargs)  
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        resultat_vehicule = []
        alert_color = " "
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            assu_all = Assurance.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            vign_all = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            stat_all = Stationnement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            
            entretiens = Entretien.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            visites = VisiteTechnique.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            reparations = Reparation.objects.filter(Q(date_saisie__lte=now) & Q(date_sortie__gte=now)).count()
            assurances = Assurance.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()

            vignette = Vignette.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()                
            patente = Patente.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()                 
            cartstation = Stationnement.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()
            for vehicule in vehicules:
                visite = VisiteTechnique.objects.filter(vehicule = vehicule).order_by('date_saisie')
                entretien = Entretien.objects.filter(vehicule = vehicule).order_by('date_saisie')
                assurances = Assurance.objects.filter(vehicule = vehicule).order_by('date_saisie')
                vignettes = Vignette.objects.filter(vehicule = vehicule).order_by('date_saisie')
                patentes = Patente.objects.filter(vehicule = vehicule).order_by('date_saisie')
                cartstaions = Stationnement.objects.filter(vehicule = vehicule).order_by('date_saisie')

                jours_cartsta_restant = cartstaions
                if jours_cartsta_restant:
                    for cartstaion in jours_cartsta_restant:
                        jours_cartsta_restant = cartstaion.jours_cartsta_restant
                        alert_cartsta_color = 'red' if jours_cartsta_restant <=10 else 'orange' if jours_cartsta_restant < 30 else 'green'
                else: 
                    jours_cartsta_restant = "0"    
                    alert_cartsta_color = "#e0e7eb"
                # 
                jours_pate_restant = patentes
                if jours_pate_restant:
                    for patente in jours_pate_restant:
                        jours_pate_restant = patente.jours_pate_restant
                        alert_pate_color = 'red' if jours_pate_restant <=10 else 'orange' if jours_pate_restant < 30 else 'green'
                else: 
                    jours_pate_restant = "0"    
                    alert_pate_color = "#e0e7eb"
                    # 
                jours_vign_restant = vignettes
                if jours_vign_restant:
                    for vignette in jours_vign_restant:
                        jours_vign_restant = vignette.jours_vign_restant
                        alert_vign_color = 'red' if jours_vign_restant <=10 else 'orange' if jours_vign_restant < 334 else 'green'
                else: 
                    jours_vign_restant = "0"    
                    alert_vign_color = "#e0e7eb"
                    # 
                jours_assu_restant = assurances
                if jours_assu_restant:
                    for assurance in jours_assu_restant:
                        jours_assu_restant = assurance.jours_assu_restant
                        alert_assu_color = 'red' if jours_assu_restant <=7 else 'orange' if jours_assu_restant < 15 else 'green'
                else: 
                    jours_assu_restant = "0"    
                    alert_assu_color = "#e0e7eb"
                    # 
                jours_ent_restant = entretien
                if jours_ent_restant:
                    for entretien in jours_ent_restant:
                        jours_ent_restant = entretien.jours_ent_restant
                        alert_ent_color = 'red' if jours_ent_restant <=3 else 'orange' if jours_ent_restant < 8 else 'green'
                else: 
                    jours_ent_restant = "0"     
                    alert_ent_color = "#e0e7eb"    
                jours_restant = visite  
                # 
                if jours_restant:       
                    for visit in jours_restant:         
                        jours_restant = visit.jour_restant      
                        alert_color = 'red' if jours_restant <=32 else 'orange' if jours_restant <92 else 'green'
                else: 
                    jours_restant = "0"    
                    alert_color = "#e0e7eb"
                def safe_int(value):
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return 0
                
                alert_types = []
                # Ajoutez les types d'alerte en fonction des jours restants
                if 1 <= safe_int(jours_restant) <= 5:
                    alert_types.append("visite technique")
                if 1 <= safe_int(jours_ent_restant) <= 5:
                    alert_types.append("entretien")
                if 1 <= safe_int(jours_assu_restant) <= 5:
                    alert_types.append("assurance")
                if 1 <= safe_int(jours_vign_restant) <= 5:
                    alert_types.append("vignette")
                if 1 <= safe_int(jours_pate_restant) <= 5:
                    alert_types.append("patente")
                if 1 <= safe_int(jours_cartsta_restant) <= 5:
                    alert_types.append("stationnement")
                # Envoie l'email d'alerte si nécessaire
                if alert_types:
                    self.send_alert_email(vehicule.immatriculation, alert_types) 
                resultat_vehicule.append({'vehicule': vehicule, 'jours_restant':jours_restant, 'alert_color':alert_color, 'alert_ent_color':alert_ent_color, 'jours_ent_restant':jours_ent_restant,'alert_assu_color':alert_assu_color,'jours_assu_restant':jours_assu_restant,'jours_vign_restant':jours_vign_restant,'alert_vign_color':alert_vign_color, 'jours_pate_restant':jours_pate_restant,'alert_pate_color':alert_pate_color, 'jours_cartsta_restant':jours_cartsta_restant,'alert_cartsta_color':alert_cartsta_color,})
            
        else:
            
            assu_all = Assurance.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            vign_all = Vignette.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            patente_all = Patente.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            stat_all = Stationnement.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            entretiens = Entretien.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            visites = VisiteTechnique.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            reparations = Reparation.objects.filter(Q(date_saisie__lte=now) & Q(date_sortie__gte=now)).count()
            assurances = Assurance.objects.filter(Q(date_saisie__lte=now) & Q(date_proch__gte=now)).count()
            vignette = Vignette.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()                
            patente = Patente.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()                 
            cartstation = Stationnement.objects.filter(Q(date__lte=now) & Q(date_proch__gte=now)).count()
            # -------------------------#-*-#------------------------- #
            for vehicule in vehicules:
                visite = VisiteTechnique.objects.filter(vehicule = vehicule).order_by('date_saisie')
                entretien = Entretien.objects.filter(vehicule = vehicule).order_by('date_saisie')
                assurances = Assurance.objects.filter(vehicule = vehicule).order_by('date_saisie')
                vignettes = Vignette.objects.filter(vehicule = vehicule).order_by('date_saisie')
                patentes = Patente.objects.filter(vehicule = vehicule).order_by('date_saisie')
                cartstaions = Stationnement.objects.filter(vehicule = vehicule).order_by('date_saisie')
                jours_cartsta_restant = cartstaions
                if jours_cartsta_restant:
                    for cartstaion in jours_cartsta_restant:
                        jours_cartsta_restant = cartstaion.jours_cartsta_restant
                        alert_cartsta_color = 'red' if jours_cartsta_restant <=10 else 'orange' if jours_cartsta_restant < 30 else 'green'
                else: 
                    jours_cartsta_restant = "0"    
                    alert_cartsta_color = "#e0e7eb"
                # 
                jours_pate_restant = patentes
                if jours_pate_restant:
                    for patente in jours_pate_restant:
                        jours_pate_restant = patente.jours_pate_restant
                        alert_pate_color = 'red' if jours_pate_restant <=10 else 'orange' if jours_pate_restant < 30 else 'green'
                else: 
                    jours_pate_restant = "0"    
                    alert_pate_color = "#e0e7eb"
                    # 
                jours_vign_restant = vignettes
                if jours_vign_restant:
                    for vignette in jours_vign_restant:
                        jours_vign_restant = vignette.jours_vign_restant
                        alert_vign_color = 'red' if jours_vign_restant <=10 else 'orange' if jours_vign_restant < 334 else 'green'
                else: 
                    jours_vign_restant = "0"    
                    alert_vign_color = "#e0e7eb"
                    # 
                jours_assu_restant = assurances
                if jours_assu_restant:
                    for assurance in jours_assu_restant:
                        jours_assu_restant = assurance.jours_assu_restant
                        alert_assu_color = 'red' if jours_assu_restant <=7 else 'orange' if jours_assu_restant < 15 else 'green'
                else: 
                    jours_assu_restant = "0"    
                    alert_assu_color = "#e0e7eb"
                    # 
                jours_ent_restant = entretien
                if jours_ent_restant:
                    for entretien in jours_ent_restant:
                        jours_ent_restant = entretien.jours_ent_restant
                        alert_ent_color = 'red' if jours_ent_restant <=3 else 'orange' if jours_ent_restant < 8 else 'green'
                else: 
                    jours_ent_restant = "0"     
                    alert_ent_color = "#e0e7eb"    
                jours_restant = visite  
                # 
                if jours_restant:       
                    for visit in jours_restant:         
                        jours_restant = visit.jour_restant      
                        alert_color = 'red' if jours_restant <=32 else 'orange' if jours_restant <92 else 'green'
                else: 
                    jours_restant = "0"    
                    alert_color = "#e0e7eb"   
                
                def safe_int(value):
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return 0
                
                alert_types = []
                # Ajoutez les types d'alerte en fonction des jours restants
                if 1 <= safe_int(jours_restant) <= 5:
                    alert_types.append("visite technique")
                if 1 <= safe_int(jours_ent_restant) <= 5:
                    alert_types.append("entretien")
                if 1 <= safe_int(jours_assu_restant) <= 5:
                    alert_types.append("assurance")
                if 1 <= safe_int(jours_vign_restant) <= 5:
                    alert_types.append("vignette")
                if 1 <= safe_int(jours_pate_restant) <= 5:
                    alert_types.append("patente")
                if 1 <= safe_int(jours_cartsta_restant) <= 5:
                    alert_types.append("stationnement")
                # Envoie l'email d'alerte si nécessaire
                if alert_types:
                    self.send_alert_email(vehicule.immatriculation, alert_types) 
                resultat_vehicule.append({'vehicule': vehicule, 'jours_restant':jours_restant, 'alert_color':alert_color, 'alert_ent_color':alert_ent_color, 'jours_ent_restant':jours_ent_restant,'alert_assu_color':alert_assu_color,'jours_assu_restant':jours_assu_restant,'jours_vign_restant':jours_vign_restant,'alert_vign_color':alert_vign_color, 'jours_pate_restant':jours_pate_restant,'alert_pate_color':alert_pate_color, 'jours_cartsta_restant':jours_cartsta_restant,'alert_cartsta_color':alert_cartsta_color,})
        context={
            'dates':dates,
            'vehicules':vehicules,
            'resultat_vehicule':resultat_vehicule,
            'annees':annee,
            'visites':visites,
            'assu_all':assu_all,
            'vign_all':vign_all,
            'pat_all':patente_all,
            'stat_all':stat_all,
            'entr_all':entretiens,
            'form':forms,
            'mois_en_cours':libelle_mois_en_cours,
        }
        return context 

class AddCategoriVehi(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):  
    login_url = 'login'
    permission_url = 'add_catego_vehi'
    model = CategoVehi      
    form_class = CategorieForm      
    template_name = 'perfect/add_categorie.html'
    success_message = 'Categorie enregistré avec succès✓✓'
    error_message = "Erreur de saisie, cette categorie ou cet identifiant existe✘✘"
    success_url= reverse_lazy('add_catego_vehi')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        messages.success(self.request,self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        catego_vehi = CategoVehi.objects.all()
        categories = catego_vehi.annotate(nb_vehicules=Count('catego_vehicule')).order_by('id')
        total_veh = Vehicule.objects.all().order_by('id').count()
        # vehicules = Vehicule.objects.filter(category=catego_vehi).order_by('id')
        forms = self.get_form()
        context = {
            'form':forms,
            'catego_vehi':catego_vehi,
            'categories':categories,
            'total_veh':total_veh,
        }
        print("",context)
        return context
    
def delete_catego(request, pk):
    try:
        catego = get_object_or_404(CategoVehi, id=pk)
        catego.delete()
        messages.success(request, f"la categorie de véhicule {catego.category} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_catego_vehi')
    
def CategoVehiculeListView(request, cid):
    categorys= CategoVehi.objects.get(cid=cid)
    cars = Vehicule.objects.filter(category=categorys)
    user_group = request.user.groups.first()
    user_group = user_group.name if user_group else None
    context = {
        'user_group':user_group,
        'categorys':categorys,
        'cars':cars,
    }
    return render(request, 'news/applist/list_vehi_categor.html',context)

class AllVehiculeView(LoginRequiredMixin, CustomPermissionRequiredMixin, View):
    login_url = 'login'
    permission_url = 'all_vehi'
    template_name = 'perfect/add_vehicule.html'
    def get(self, request, pk=None):
        # Chargement des catégories avec le nombre de véhicules
        categories = CategoVehi.objects.annotate(nb_vehicules=Count('catego_vehicule')).order_by('id')
        vehicules = Vehicule.objects.none()
        cout_totals = 0
        total_veh = 0
        categorie = None
        if pk:
            categorie = get_object_or_404(CategoVehi, pk=pk)
            vehicules = Vehicule.objects.filter(category=categorie).order_by('id')
            cout_totals = vehicules.aggregate(total=Sum('cout_acquisition'))['total'] or 0
            cout_total = '{:,}'.format(cout_totals).replace('',' ')
            total_veh = vehicules.count()
        else:
            vehicules = Vehicule.objects.all().order_by('id')
            cout_totals = vehicules.aggregate(total=Sum('cout_acquisition'))['total'] or 0
            cout_total = '{:,}'.format(cout_totals).replace('',' ')
            total_veh = vehicules.count()
        return render(request, self.template_name, {
            'vehicules': vehicules,
            'categorie': categorie,
            'categories': categories,
            'cout_total': cout_total,
            'total_veh': total_veh

        })

class AddVehiculeExcelView(View, LoginRequiredMixin,):
    login_url = 'login'
    # permission_url = 'add_car'
    template_name = 'perfect/add_vehicule.html'
    success_message = 'Véhicule enregistré avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘"
    def get(self, request, pk=None):
        cout_totals = 0
        total_veh = 0
        categories = CategoVehi.objects.annotate(nb_vehicules=Count('catego_vehicule')).order_by('id')
        if pk:
            categorie = get_object_or_404(CategoVehi, pk=pk)
            vehicules = Vehicule.objects.filter(category=categorie).order_by('id')
            cout_totals = vehicules.aggregate(total=Sum('cout_acquisition'))['total'] or 0
            cout_total = '{:,}'.format(cout_totals).replace('',' ')

            total_veh = vehicules.count()
            form = VehiculeForm()
        else:
            categorie = None
            vehicules = Vehicule.objects.none()
            cout_totals = vehicules.aggregate(total=Sum('cout_acquisition'))['total'] or 0
            cout_total = '{:,}'.format(cout_totals).replace('',' ')
            total_veh = vehicules.count()
            form = VehiculeForm()
        return render(request, self.template_name, {
            'forms': form,
            'vehicules': vehicules,
            'categorie': categorie,
            'categories': categories,
            'cout_total': cout_total,
            'total_veh': total_veh,
        })
    def post(self, request, pk=None):
        categorie = get_object_or_404(CategoVehi, pk=pk)
        categories = CategoVehi.objects.all().order_by('id')
        if request.FILES.get('excel_file'):
            excel_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(excel_file)
                required_columns = [
                    'immatriculation', 'marque', 'duree', 'num_cart_grise',
                    'num_Chassis', 'date_acquisition', 'cout_acquisition',
                    'dat_edit_carte_grise', 'date_mis_service', 
                ]
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f"Colonnes manquantes : {', '.join(missing_columns)}")
                    return redirect('add_vehi', pk=pk)
                created_count = 0
                updated_count = 0
                for _, row in df.iterrows():
                    immatriculation = str(row['immatriculation']).strip()
                    if not immatriculation:
                        continue  
                    vehicule_data = {
                        'marque': str(row.get('marque', '')).strip(),
                        'duree': int(row.get('duree', 0)),
                        'num_cart_grise': str(row.get('num_cart_grise')).strip(),
                        'num_Chassis': str(row.get('num_Chassis')).strip(),
                        'date_acquisition': pd.to_datetime(row.get('date_acquisition')).date(),
                        'cout_acquisition': int(row.get('cout_acquisition', 0)),
                        'dat_edit_carte_grise': pd.to_datetime(row.get('dat_edit_carte_grise')).date(),
                        'date_mis_service': pd.to_datetime(row.get('date_mis_service')).date(),
                        'category': categorie,
                        'auteur': request.user,
                    }
                    vehicule, created = Vehicule.objects.update_or_create(
                        immatriculation=immatriculation,
                        defaults=vehicule_data
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                messages.success(request, f"✅ {created_count} véhicule(s) créé(s), {updated_count} mis à jour.")
                return redirect('add_vehi', pk=pk)

            except Exception as e:
                messages.error(request, f"Erreur d'importation vérifier les informations du fichier Excel ")
                return redirect('add_vehi', pk=pk)
        # Traitement manuel du formulaire
        form = VehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            vehicule = form.save(commit=False)
            vehicule.auteur = request.user
            vehicule.category = categorie
            vehicule.save()
            messages.success(request, self.success_message)
            return redirect('all_vehi')
        else:
            messages.error(request, self.error_message)
            vehicules = Vehicule.objects.filter(category=categorie).order_by('-id')
            cout_total = vehicules.aggregate(total=Sum('cout_acquisition'))['total'] or 0
            total_veh = vehicules.count()
            return render(request, self.template_name, {
                'forms': form,
                'vehicules': vehicules,
                'categorie': categorie,
                'categories': categories,
                'cout_total': cout_total,
                'total_veh': total_veh,
            })

def delete_vehicule(request, pk):
    try:
        vehicule = get_object_or_404(Vehicule, id=pk)
        vehicule.delete()
        messages.success(request, f"le véhicule {vehicule.immatriculation} - {vehicule.marque} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_vehi', pk=vehicule.category.id if vehicule.category else None)

# @require_POST
@login_required(login_url='login')
def delete_multiple_vehicules(request):
    ids = request.POST.getlist('vehicule_ids')
    if ids:
        vehicules = Vehicule.objects.filter(id__in=ids)
        deleted_count = vehicules.count()
        vehicules.delete()
        messages.success(request, f"{deleted_count} véhicule(s) supprimé(s) avec succès.")
    else:
        messages.warning(request, "Aucun véhicule sélectionné.")
    return redirect('all_vehi')

class UpdatVehiculeView(LoginRequiredMixin, UpdateView):
    model = Vehicule
    login_url = 'login'
    form_class = UpdatVehiculeForm
    template_name = 'perfect/car_update.html'
    success_message = 'véhicule Modifié avec succès✓✓'
    error_message = "Erreur de saisie un véhicule enregistré utilise déjà des informations verifié l'immatriculation, Numero chassis ou la carte grise ✘✘ "
    # success_url = reverse_lazy ('listvehi')
    timeout_minutes = 300
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        reponse = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicules = Vehicule.objects.all()
        context.update({
            'vehicules':vehicules,
        })
        return context
    def get_success_url(self):
        return reverse('updatecar', kwargs={'pk': self.kwargs['pk']})

class DashboardGaragView(CustomPermissionRequiredMixin, TemplateView):
    model = Vehicule
    template_name = 'perfect/dash_garag.html'
    permission_url = 'dashgarage'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        else:
            vehicules = Vehicule.objects.all()
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            
            nb_reparatvtc = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin], vehicule__category__category ='VTC').count()
            total_reparatvtc = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin], vehicule__category__category ='VTC').aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparatvtc_format ='{:,}'.format(total_reparatvtc).replace('',' ')
            
            nb_reparataxi = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin], vehicule__category__category ='TAXI').count()
            total_reparataxi = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin], vehicule__category__category ='TAXI').aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparataxi_format ='{:,}'.format(total_reparataxi).replace('',' ')
            
            nb_reparat = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin]).count()
            total_reparat = Reparation.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparat_format ='{:,}'.format(total_reparat).replace('',' ')
            
            total_visit = VisiteTechnique.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_visit_format ='{:,}'.format(total_visit).replace('',' ')
            
            total_entret = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_ent_format ='{:,}'.format(total_entret).replace('',' ')
            
            total_piece = Piece.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            
            total_piecechang = PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piececha_format ='{:,}'.format(total_piecechang).replace('',' ')
            
            total_piece_int = Piece.objects.filter(date_saisie__range=[date_debut, date_fin], lieu="INTERNE").aggregate(somme=Sum('montant'))['somme'] or 0
            total_piecechang_int = PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin], lieu="INTERNE").aggregate(somme=Sum('montant'))['somme'] or 0
            total_pieces_int = total_piece_int + total_piecechang_int
            total_pieces_format_int = '{:,}'.format(total_pieces_int).replace('',' ')
            
            total_patent = Patente.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_pat_format ='{:,}'.format(total_patent).replace('',' ')
            
            total_statio = Stationnement.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_sta_format ='{:,}'.format(total_statio).replace('',' ')
            
            total_vigne = Vignette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_vign_format ='{:,}'.format(total_vigne).replace('',' ')
            
            ################################----Graphiques----#############################
            rep_vtc_data = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in rep_vtc_data:
                rep_mois_vtc_data[commande.date_saisie.month] += commande.montant
            rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
            
            rep_taxi_data = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            rep_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in rep_taxi_data:
                rep_mois_taxi_data[commande.date_saisie.month] += commande.montant
            rep_mois_taxi_data = [rep_mois_taxi_data[month] for month in range(1, 13)]
            
            vis_vtc_data = VisiteTechnique.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            vis_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in vis_vtc_data:
                vis_mois_vtc_data[commande.date_saisie.month] += commande.montant
            vis_mois_vtc_data = [vis_mois_vtc_data[month] for month in range(1, 13)]
            vis_taxi_data = VisiteTechnique.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            vis_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in vis_taxi_data:
                vis_mois_taxi_data[commande.date_saisie.month] += commande.montant
            vis_mois_taxi_data = [vis_mois_taxi_data[month] for month in range(1, 13)]
            
            ent_vtc_data = Entretien.objects.filter(vehicule__category__category="VTC", date_saisie__range=[date_debut, date_fin])
            ent_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in ent_vtc_data:
                ent_mois_vtc_data[commande.date_saisie.month] += commande.montant
            ent_mois_vtc_data = [ent_mois_vtc_data[month] for month in range(1, 13)]
            
            ent_taxi_data = Entretien.objects.filter(vehicule__category__category="TAXI", date_saisie__range=[date_debut, date_fin])
            ent_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in ent_taxi_data:
                ent_mois_taxi_data[commande.date_saisie.month] += commande.montant
            ent_mois_taxi_data = [ent_mois_taxi_data[month] for month in range(1, 13)]
            
            piec_vtc_data = Piece.objects.filter(reparation__in=rep_vtc_data,date_saisie__range=[date_debut, date_fin])
            piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piec_vtc_data:
                piec_mois_vtc_data[commande.date_saisie.month] += commande.montant
            piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
            piec_taxi_data = Piece.objects.filter(reparation__in=rep_taxi_data,date_saisie__range=[date_debut, date_fin])
            piec_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piec_taxi_data:
                piec_mois_taxi_data[commande.date_saisie.month] += commande.montant
            piec_mois_taxi_data = [piec_mois_taxi_data[month] for month in range(1, 13)]
            
            piecha_vtc_data = PiecEchange.objects.filter(vehicule__category__category="VTC",date_saisie__range=[date_debut, date_fin])
            piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_vtc_data:
                piecha_mois_vtc_data[commande.date_saisie.month] += commande.montant
            piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
            piecha_taxi_data = PiecEchange.objects.filter(vehicule__category__category="TAXI",date_saisie__range=[date_debut, date_fin])
            piecha_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_taxi_data:
                piecha_mois_taxi_data[commande.date_saisie.month] += commande.montant
            piecha_mois_taxi_data = [piecha_mois_taxi_data[month] for month in range(1, 13)]
            
        else:
            nb_reparat = Reparation.objects.filter(date_saisie__month=date.today().month).count()
            total_reparat = Reparation.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparat_format ='{:,}'.format(total_reparat).replace('',' ')
            
            nb_reparatvtc = Reparation.objects.filter(date_saisie__month=date.today().month, vehicule__category__category ='VTC').count()
            total_reparatvtc = Reparation.objects.filter(date_saisie__month=date.today().month, vehicule__category__category ='VTC').aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparatvtc_format ='{:,}'.format(total_reparatvtc).replace('',' ')
            
            nb_reparataxi = Reparation.objects.filter(date_saisie__month=date.today().month, vehicule__category__category ='TAXI').count()
            total_reparataxi = Reparation.objects.filter(date_saisie__month=date.today().month, vehicule__category__category ='TAXI').aggregate(somme=Sum('montant'))['somme'] or 0
            total_reparataxi_format ='{:,}'.format(total_reparataxi).replace('',' ')
            
            total_visit = VisiteTechnique.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_visit_format ='{:,}'.format(total_visit).replace('',' ')
            
            total_entret = Entretien.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_ent_format ='{:,}'.format(total_entret).replace('',' ')
            
            total_piece = Piece.objects.filter(date_saisie__month=date.today().month,).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            
            total_piecechang = PiecEchange.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piececha_format ='{:,}'.format(total_piecechang).replace('',' ')
            
            total_piece_int = Piece.objects.filter(date_saisie__month=date.today().month, lieu="INTERNE").aggregate(somme=Sum('montant'))['somme'] or 0
            total_piecechang_int = PiecEchange.objects.filter(date_saisie__month=date.today().month, lieu="INTERNE").aggregate(somme=Sum('montant'))['somme'] or 0
            total_pieces_int = total_piece_int + total_piecechang_int
            total_pieces_format_int = '{:,}'.format(total_pieces_int).replace('',' ')
            
            total_patent = Patente.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_pat_format ='{:,}'.format(total_patent).replace('',' ')
            
            total_statio = Stationnement.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_sta_format ='{:,}'.format(total_statio).replace('',' ')
            
            total_vigne = Vignette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_vign_format ='{:,}'.format(total_vigne).replace('',' ')
            
            ################################----Graphiques----#############################
            rep_vtc_data = Reparation.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            rep_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in rep_vtc_data:
                rep_mois_vtc_data[commande.date_saisie.month] += commande.montant
            rep_mois_vtc_data = [rep_mois_vtc_data[month] for month in range(1, 13)]
            
            rep_taxi_data = Reparation.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            rep_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in rep_taxi_data:
                rep_mois_taxi_data[commande.date_saisie.month] += commande.montant
            rep_mois_taxi_data = [rep_mois_taxi_data[month] for month in range(1, 13)]
            
            vis_vtc_data = VisiteTechnique.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            vis_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in vis_vtc_data:
                vis_mois_vtc_data[commande.date_saisie.month] += commande.montant
            vis_mois_vtc_data = [vis_mois_vtc_data[month] for month in range(1, 13)]
            vis_taxi_data = VisiteTechnique.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            vis_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in vis_taxi_data:
                vis_mois_taxi_data[commande.date_saisie.month] += commande.montant
            vis_mois_taxi_data = [vis_mois_taxi_data[month] for month in range(1, 13)]
            
            ent_vtc_data = Entretien.objects.filter(vehicule__category__category="VTC", date_saisie__year=datetime.now().year)
            ent_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in ent_vtc_data:
                ent_mois_vtc_data[commande.date_saisie.month] += commande.montant
            ent_mois_vtc_data = [ent_mois_vtc_data[month] for month in range(1, 13)]
            
            ent_taxi_data = Entretien.objects.filter(vehicule__category__category="TAXI", date_saisie__year=datetime.now().year)
            ent_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in ent_taxi_data:
                ent_mois_taxi_data[commande.date_saisie.month] += commande.montant
            ent_mois_taxi_data = [ent_mois_taxi_data[month] for month in range(1, 13)]
            
            piec_vtc_data = Piece.objects.filter(reparation__in=rep_vtc_data,date_saisie__year=datetime.now().year)
            piec_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piec_vtc_data:
                piec_mois_vtc_data[commande.date_saisie.month] += commande.montant
            piec_mois_vtc_data = [piec_mois_vtc_data[month] for month in range(1, 13)]
            piec_taxi_data = Piece.objects.filter(reparation__in=rep_taxi_data,date_saisie__year=datetime.now().year)
            piec_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piec_taxi_data:
                piec_mois_taxi_data[commande.date_saisie.month] += commande.montant
            piec_mois_taxi_data = [piec_mois_taxi_data[month] for month in range(1, 13)]
            
            piecha_vtc_data = PiecEchange.objects.filter(vehicule__category__category="VTC",date_saisie__year=datetime.now().year)
            piecha_mois_vtc_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_vtc_data:
                piecha_mois_vtc_data[commande.date_saisie.month] += commande.montant
            piecha_mois_vtc_data = [piecha_mois_vtc_data[month] for month in range(1, 13)]
            piecha_taxi_data = PiecEchange.objects.filter(vehicule__category__category="TAXI",date_saisie__year=datetime.now().year)
            piecha_mois_taxi_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_taxi_data:
                piecha_mois_taxi_data[commande.date_saisie.month] += commande.montant
            piecha_mois_taxi_data = [piecha_mois_taxi_data[month] for month in range(1, 13)]
            
        context.update({
                'rep_mois_vtc_data':rep_mois_vtc_data,
                'rep_mois_taxi_data':rep_mois_taxi_data,
                
                'vis_mois_vtc_data':vis_mois_vtc_data,
                'vis_mois_taxi_data':vis_mois_taxi_data,
                
                'ent_mois_vtc_data':ent_mois_vtc_data,
                'ent_mois_taxi_data':ent_mois_taxi_data,
                
                'piec_mois_vtc_data':piec_mois_vtc_data,
                'piec_mois_taxi_data':piec_mois_taxi_data,
                
                'piecha_mois_vtc_data':piecha_mois_vtc_data,
                'piecha_mois_taxi_data':piecha_mois_taxi_data,
                
                'nb_reparat':nb_reparat,
                'total_reparat_format':total_reparat_format,
                'total_visit_format':total_visit_format,
                'total_ent_format':total_ent_format,
                'total_piece_format':total_piece_format,
                'total_piececha_format':total_piececha_format,
                'total_pat_format':total_pat_format,
                'total_sta_format':total_sta_format,
                'total_vign_format':total_vign_format, 
                
                'nb_reparatvtc':nb_reparatvtc,
                'total_reparatvtc_format':total_reparatvtc_format,

                'nb_reparataxi':nb_reparataxi,
                'total_reparataxi_format':total_reparataxi_format,
                'total_pieces_format_int':total_pieces_format_int,
                
                'labels':label,
                'form':form,
                'dates':dates,
                'vehicules':vehicules  
            })
        return context 

class DashboardGaragecarView(LoginRequiredMixin, DetailView):
    model = Vehicule
    login_url = 'login'
    template_name = 'perfect/dash_garag_car.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        label = [calendar.month_name[month][:1] for month in range(1, 13)]
        context['catego_vehi'] = CategoVehi.objects.all()
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        else:
            vehicules = Vehicule.objects.all()
        vehicule = self.get_object()
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin'] 
            reparations_mois = Reparation.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin])
            reparations = Reparation.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            visitechniques = VisiteTechnique.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            entretiens = Entretien.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            piecerep = Piece.objects.filter(reparation__in = reparations_mois).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            vignettes = Vignette.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            patentes = Patente.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            stations = Stationnement.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            
            tot_reparation = Reparation.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).count()
            tot_piecerep_int = Piece.objects.filter(reparation__in = reparations_mois, date_saisie__range=[date_debut, date_fin], lieu='INTERNE').count()
            tot_piece_cout_int = Piece.objects.filter(reparation__in = reparations_mois, date_saisie__range=[date_debut, date_fin], lieu='INTERNE').aggregate(Sum('montant'))['montant__sum'] or 0
            tot_piechange = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin]).count()
            
            ###########################################################################################################################################################
            rep_data = Reparation.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin])
            rep_mois_data = {month: 0 for month in range(1, 13)}
            for commande in rep_data:
                rep_mois_data[commande.date_saisie.month] += commande.montant
            rep_mois_data = [rep_mois_data[month] for month in range(1, 13)]
            
            entret_data = Entretien.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin])
            entret_mois_data = {month: 0 for month in range(1, 13)}
            for commande in entret_data:
                entret_mois_data[commande.date_saisie.month] += commande.montant
            entret_mois_data = [entret_mois_data[month] for month in range(1, 13)]
            
            piece_data = Piece.objects.filter(reparation__in=rep_data, date_saisie__range=[date_debut, date_fin])
            piece_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piece_data:
                piece_mois_data[commande.date_saisie.month] += commande.montant
            piece_mois_data = [piece_mois_data[month] for month in range(1, 13)]
            
            piecha_data = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__range=[date_debut, date_fin])
            piecha_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_data:
                piecha_mois_data[commande.date_saisie.month] += commande.montant
            piecha_mois_data = [piecha_mois_data[month] for month in range(1, 13)]
            
        else:
            reparations_mois = Reparation.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month)
            reparations = Reparation.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            visitechniques = VisiteTechnique.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            entretiens = Entretien.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piecerep = Piece.objects.filter(reparation__in = reparations_mois).aggregate(somme=Sum('montant'))['somme'] or 0
            piechang = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            vignettes = Vignette.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(Sum('montant'))['montant__sum'] or 0
            patentes = Patente.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(Sum('montant'))['montant__sum'] or 0
            stations = Stationnement.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).aggregate(Sum('montant'))['montant__sum'] or 0
            
            tot_reparation = Reparation.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).count()
            tot_piecerep_int = Piece.objects.filter(reparation__in = reparations_mois, date_saisie__month=date.today().month, lieu='INTERNE').count()
            tot_piece_cout_int = Piece.objects.filter(reparation__in = reparations_mois, date_saisie__month=date.today().month, lieu='INTERNE').aggregate(Sum('montant'))['montant__sum'] or 0
            tot_piechange = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__month=date.today().month).count()
            
            ###########################################################################################################################################################
            rep_data = Reparation.objects.filter(vehicule = vehicule, date_saisie__year=datetime.now().year)
            rep_mois_data = {month: 0 for month in range(1, 13)}
            for commande in rep_data:
                rep_mois_data[commande.date_saisie.month] += commande.montant
            rep_mois_data = [rep_mois_data[month] for month in range(1, 13)]
            
            entret_data = Entretien.objects.filter(vehicule = vehicule, date_saisie__year=datetime.now().year)
            entret_mois_data = {month: 0 for month in range(1, 13)}
            for commande in entret_data:
                entret_mois_data[commande.date_saisie.month] += commande.montant
            entret_mois_data = [entret_mois_data[month] for month in range(1, 13)]
            
            piece_data = Piece.objects.filter(reparation__in=rep_data, date_saisie__year=datetime.now().year)
            piece_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piece_data:
                piece_mois_data[commande.date_saisie.month] += commande.montant
            piece_mois_data = [piece_mois_data[month] for month in range(1, 13)]
            
            piecha_data = PiecEchange.objects.filter(vehicule = vehicule, date_saisie__year=datetime.now().year)
            piecha_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piecha_data:
                piecha_mois_data[commande.date_saisie.month] += commande.montant
            piecha_mois_data = [piecha_mois_data[month] for month in range(1, 13)]
            
        context.update({
                'reparations':reparations,
                'visitechniques':visitechniques,
                'entretiens':entretiens,
                'piecerep':piecerep,
                'piechang':piechang,
                'vignettes':vignettes,
                'patentes':patentes,
                'stations':stations,
                
                'tot_reparation':tot_reparation,
                'tot_piecerep_int':tot_piecerep_int,
                'tot_piece_cout_int':tot_piece_cout_int,
                'tot_piechange':tot_piechange,
                'vehicule':vehicule,
                'vehicules':vehicules,
                ####################Graphe##################
                'rep_mois_data':rep_mois_data,
                'entret_mois_data':entret_mois_data,
                'piece_mois_data':piece_mois_data,
                'piecha_mois_data':piecha_mois_data,
                'label':label,
                'form':form,
        })
        return context 
        
class CarFinanceView(LoginRequiredMixin, CustomPermissionRequiredMixin,TemplateView):
    login_url = 'login'
    permission_url = 'detail_car_financier'
    model = Vehicule
    template_name = 'perfect/dash_car.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        context={
            'vehicule':vehicules,
        }
        return context

class DetailVehiculeView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Vehicule
    template_name = 'perfect/dash_car.html'
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
        label = [calendar.month_name[month][:1] for month in range(1, 13)]

        vehicule = Vehicule.objects.all()
        vehicules = self.get_object()
        form = DateForm(self.request.GET)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'] 
            date_fin = form.cleaned_data['date_fin']
            
            recettes = Recette.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1 
            charge_var = ChargeVariable.objects.filter(vehicule = vehicules, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            charge_fix = ChargeFixe.objects.filter(vehicule = vehicules, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            piecechang = PiecEchange.objects.filter(vehicule = vehicules, date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            Total_charge = charge_fix + charge_var
            marg_contr = recettes - charge_var
            taux_marge = (marg_contr*100/(recettes))
            taux_marge_format='{:.2f}'.format(taux_marge)
            resultat = recettes-Total_charge

            nbreparation = Reparation.objects.filter(date_entree__range=[date_debut, date_fin], vehicule = vehicules).count() 
            reparations = Reparation.objects.filter(date_entree__range=[date_debut, date_fin],vehicule = vehicules)
            som_piece = Piece.objects.filter(reparation__in=reparations).aggregate(somme=Sum('montant'))['somme'] or 0
            
            ################################----Graphiques----#############################
            recet_data = Recette.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin])
            recet_mois_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data:
                recet_mois_data[commande.date_saisie.month] += commande.montant
            recet_mois_data = [recet_mois_data[month] for month in range(1, 13)]
            
            chargfix_data = ChargeFixe.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin])
            chargfix_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_data:
                chargfix_mois_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_data = [chargfix_mois_data[month] for month in range(1, 13)]
            
            chargvar_data = ChargeVariable.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin])
            chargvar_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_data:
                chargvar_mois_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
            
            reparations = Reparation.objects.filter(date_entree__range=[date_debut, date_fin],vehicule = vehicules)
            piece_data = Piece.objects.filter(reparation__in = reparations)
            piece_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piece_data:
                piece_mois_data[commande.date_saisie.month] += commande.montant
            piece_mois_data = [piece_mois_data[month] for month in range(1, 13)]
            
            piechag_data = PiecEchange.objects.filter(vehicule=vehicules, date_saisie__range=[date_debut, date_fin])
            piechang_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piechag_data:
                piechang_mois_data[commande.date_saisie.month] += commande.montant
            piechang_mois_data = [piechang_mois_data[month] for month in range(1, 13)]
            
            # label = [calendar.month_name[month][:1] for month in range(1, 13)]
            
            # marges_mensuelles = recet_mois_data - chargvar_mois_data
            marge_data = [recet_mois_data[i] - chargvar_mois_data[i] for i in range(12)]
            # Calcul des taux mensuels
            taux_data = [(marge_data[i] * 100) / recet_mois_data[i] if recet_mois_data[i] > 0 else 0 for i in range(12)]
        else:
            recettes = Recette.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            charge_fix = ChargeFixe.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            charge_var = ChargeVariable.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            piecechang = PiecEchange.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0

            Total_charge = charge_fix + charge_var
            marg_contr = recettes - charge_var
            taux_marge = (marg_contr*100/(recettes))
            
            taux_marge_format='{:.2f}'.format(taux_marge)
            resultat = recettes-Total_charge
            
            
            nbreparation = Reparation.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month).count()
            reparations = Reparation.objects.filter(vehicule = vehicules, date_saisie__month=date.today().month)
            som_piece = Piece.objects.filter(reparation__in = reparations).aggregate(somme=Sum('montant'))['somme'] or 0
            
            # reparation_mois = Reparation.objects.filter(vehicule = vehicule).annotate(month=ExtractMonth("date_entree")).values("month").annotate(total=Count("id")).values("month","total").order_by('month')

            recet_data = Recette.objects.filter(vehicule=vehicules, date_saisie__month=date.today().month)
            recet_mois_data = {month: 0 for month in range(1, 13)}
            for commande in recet_data:
                recet_mois_data[commande.date_saisie.month] += commande.montant
            recet_mois_data = [recet_mois_data[month] for month in range(1, 13)]
            
            chargfix_data = ChargeFixe.objects.filter(vehicule=vehicules, date_saisie__month=date.today().month)
            chargfix_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargfix_data:
                chargfix_mois_data[commande.date_saisie.month] += commande.montant
            chargfix_mois_data = [chargfix_mois_data[month] for month in range(1, 13)]
            
            chargvar_data = ChargeVariable.objects.filter(vehicule=vehicules, date_saisie__month=date.today().month)
            chargvar_mois_data = {month: 0 for month in range(1, 13)}
            for commande in chargvar_data:
                chargvar_mois_data[commande.date_saisie.month] += commande.montant
            chargvar_mois_data = [chargvar_mois_data[month] for month in range(1, 13)]
            
            piechag_data = PiecEchange.objects.filter(vehicule=vehicules, date_saisie__month=date.today().month)
            piechang_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piechag_data:
                piechang_mois_data[commande.date_saisie.month] += commande.montant
            piechang_mois_data = [piechang_mois_data[month] for month in range(1, 13)]
            
            reparations = Reparation.objects.filter(vehicule = vehicules,date_saisie__month=date.today().month)
            piece_data = Piece.objects.filter(reparation__in = reparations)
            piece_mois_data = {month: 0 for month in range(1, 13)}
            for commande in piece_data:
                piece_mois_data[commande.date_saisie.month] += commande.montant
            piece_mois_data = [piece_mois_data[month] for month in range(1, 13)]

            marge_data = [recet_mois_data[i] - chargvar_mois_data[i] for i in range(12)]

            # Calcul des taux mensuels
            taux_data = [(marge_data[i] * 100) / recet_mois_data[i] if recet_mois_data[i] > 0 else 0 for i in range(12)]

        context.update({
            'recettes':recettes,
            'charge_fix':charge_fix,
            'charge_var':charge_var,
            # 'taux_marge':taux_marge,
            'taux_marge_format':taux_marge_format,
            'resultat':resultat,
            'nbreparation':nbreparation,
            'resultat':resultat,
            'som_piece':som_piece,
            'piecechang':piecechang,
            
            'recet_mois_data':recet_mois_data,
            'chargfix_mois_data':chargfix_mois_data,
            'chargvar_mois_data':chargvar_mois_data,
            'piece_mois_data':piece_mois_data,
            'piechang_mois_data':piechang_mois_data,
            
            'taux_data':taux_data,
            
            'dates':dates,
            'vehicules':vehicules,
            'vehicule':vehicule,
            'annees':annee,
            'mois_en_cours':libelle_mois_en_cours,
            
            'form':form,
            'labels':label,
        })    
        return context 
    
class SaisieGaragView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    login_url = 'login'
    permission_url = 'saisi_garag'
    template_name = 'perfect/saisi_garag.html'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        user = self.request.user
        # Define the filtering based on user type and gerant_voiture condition
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        assure_queryset = Assurance.objects.all()
        vigne_queryset = Vignette.objects.all()
        patent_queryset = Patente.objects.all()
        station_queryset = Stationnement.objects.all()
        piechang_queryset = PiecEchange.objects.all()

        form = self.form_class(self.request.GET)

        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            
        if categorie_filter:
            assure_queryset = assure_queryset.filter(vehicule__category__category=categorie_filter)
            vigne_queryset = vigne_queryset.filter(vehicule__category__category=categorie_filter)
            patent_queryset = patent_queryset.filter(vehicule__category__category=categorie_filter)
            station_queryset = station_queryset.filter(vehicule__category__category=categorie_filter)
            piechang_queryset = piechang_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            assure_queryset = assure_queryset.filter(date_saisie__range=[date_debut, date_fin])
            vigne_queryset = vigne_queryset.filter(date_saisie__range=[date_debut, date_fin])
            patent_queryset = patent_queryset.filter(date_saisie__range=[date_debut, date_fin])
            station_queryset = station_queryset.filter(date_saisie__range=[date_debut, date_fin])
            piechang_queryset = piechang_queryset.filter(date_saisie__range=[date_debut, date_fin])

        assure_mois = assure_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        assure_mois_format ='{:,}'.format(assure_mois).replace('',' ')

        vigne_mois = vigne_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        vigne_mois_format ='{:,}'.format(vigne_mois).replace('',' ')

        patent_mois = patent_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        patent_mois_format ='{:,}'.format(patent_mois).replace('',' ')

        station_mois = station_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        station_mois_format ='{:,}'.format(station_mois).replace('',' ')

        piechang_mois = piechang_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        piechang_mois_format ='{:,}'.format(piechang_mois).replace('',' ')
        
        context={

            'vehicules':vehicules,
            'assure_mois_format':assure_mois_format,
            'vigne_mois_format':vigne_mois_format,
            'patent_mois_format':patent_mois_format,
            'station_mois_format':station_mois_format,
            'piechang_mois_format':piechang_mois_format,
            
            'form':form,
        }
        return context


class TempsArretsView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    login_url = 'login'
    permission_url = 'temps_arrets'
    template_name = 'perfect/saisi_temp_arret.html'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()
        else:
            vehicules = Vehicule.objects.all()
        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()
        
        visit_queryset = VisiteTechnique.objects.all()
        entretien_queryset = Entretien.objects.all()
        reparat_queryset = Reparation.objects.all()
        autarret_queryset = Autrarret.objects.all()

        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            
        if categorie_filter:
            visit_queryset = visit_queryset.filter(vehicule__category__category=categorie_filter)
            entretien_queryset = entretien_queryset.filter(vehicule__category__category=categorie_filter)
            reparat_queryset = reparat_queryset.filter(vehicule__category__category=categorie_filter)
            autarret_queryset = autarret_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            visit_queryset = visit_queryset.filter(date_saisie__range=[date_debut, date_fin])
            entretien_queryset = entretien_queryset.filter(date_saisie__range=[date_debut, date_fin])
            reparat_queryset = reparat_queryset.filter(date_saisie__range=[date_debut, date_fin])
            autarret_queryset = autarret_queryset.filter(date_saisie__range=[date_debut, date_fin])

        total_visit = visit_queryset.filter(date_saisie__month=date.today().month).count()
        total_entretien = entretien_queryset.filter(date_saisie__month=date.today().month).count()
        total_reparat = reparat_queryset.filter(date_saisie__month=date.today().month).count()
        total_autarret = autarret_queryset.filter(date_saisie__month=date.today().month).count()

        visit_mois = visit_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        visit_mois_format ='{:,}'.format(visit_mois).replace('',' ')

        entretien_mois = entretien_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        entretien_mois_format ='{:,}'.format(entretien_mois).replace('',' ')

        reparat_mois = reparat_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        reparat_mois_format ='{:,}'.format(reparat_mois).replace('',' ')

        autarret_mois = autarret_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        autarret_mois_format ='{:,}'.format(autarret_mois).replace('',' ')

        context.update({
            'dates': dates,
            'vehicules': vehicules, 
            'total_visit': total_visit,
            'total_entretien': total_entretien,
            'total_reparat': total_reparat,
            'total_autarret': total_autarret,
            'visit_mois': visit_mois,
            'visit_mois_format': visit_mois_format,
            'entretien_mois_format': entretien_mois_format,
            'reparat_mois_format': reparat_mois_format,
            'autarret_mois_format': autarret_mois_format,
            'form': form,
            'search_query': search_query,  # pour réafficher la recherche
        })
        return context

class SaisiComptaView(LoginRequiredMixin, CustomPermissionRequiredMixin,TemplateView):
    login_url = 'login'
    permission_url = 'saisi_compta'
    template_name = 'perfect/saisi_comptable.html'
    timeout_minutes = 120
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        
        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        recette_queryset = Recette.objects.all()
        chargvariale_queryset = ChargeVariable.objects.all()
        chargefixe_queryset = ChargeFixe.objects.all()

        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            
        if categorie_filter:
            recette_queryset = recette_queryset.filter(vehicule__category__category=categorie_filter)
            chargvariale_queryset = chargvariale_queryset.filter(vehicule__category__category=categorie_filter)
            chargefixe_queryset = chargefixe_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:

            recette_queryset = recette_queryset.filter(date_saisie__range=[date_debut, date_fin])
            chargvariale_queryset = chargvariale_queryset.filter(date_saisie__range=[date_debut, date_fin])
            chargefixe_queryset = chargefixe_queryset.filter(date_saisie__range=[date_debut, date_fin])
        
        recette_mois = recette_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        recette_mois_format ='{:,}'.format(recette_mois).replace('',' ')

        chargvariale_mois = chargvariale_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        chargvariale_mois_format ='{:,}'.format(chargvariale_mois).replace('',' ')

        chargefixe_mois = chargefixe_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        chargefixe_mois_format ='{:,}'.format(chargefixe_mois).replace('',' ')

        chargtot_mois = chargefixe_mois + chargvariale_mois
        chargtot_mois_format ='{:,}'.format(chargtot_mois).replace('',' ')

        margcontrib_mois = recette_mois - chargtot_mois
        margcontrib_mois_format ='{:,}'.format(margcontrib_mois).replace('',' ')

        if recette_mois == 0:
            taux_marge_mois = 0
        else:
            taux_marge_mois = (margcontrib_mois*100/(recette_mois))
        taux_marge_mois_format ='{:.2f}'.format(taux_marge_mois).replace('',' ')

        result_mois = recette_mois - chargtot_mois
        result_mois_format ='{:,}'.format(result_mois).replace('',' ')
        
        context={
            'dates':dates,
            'vehicules':vehicules,
            'recette_mois_format':recette_mois_format,
            'chargvariale_mois_format':chargvariale_mois_format,
            'chargefixe_mois_format':chargefixe_mois_format,
            'chargtot_mois_format':chargtot_mois_format,
            'margcontrib_mois_format':margcontrib_mois_format,
            'taux_marge_mois_format':taux_marge_mois_format,
            'result_mois_format':result_mois_format,
            
            'form':form,
        }
        return context

#------------------------------COMPTABLE-------------------------------
class AddRecetteView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_recettes'
    model = Recette
    form_class = RecetteForm
    template_name= "perfect/add_recet.html"
    success_message = 'Recette Ajoutée avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        recette_queryset = Recette.objects.filter(vehicule=vehicule)
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            recette_queryset = recette_queryset.filter(date_saisie__range=[date_debut, date_fin])

        recette_jours = recette_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        recette_jours_format ='{:,}'.format(recette_jours).replace('',' ')
        recette_mois = recette_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        recette_mois_format ='{:,}'.format(recette_mois).replace('',' ')
        recette_an = recette_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        recette_an_format ='{:,}'.format(recette_an).replace('',' ')
        liste_recette = recette_queryset.filter(date_saisie__month=date.today().month)

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "recette_jours_format": recette_jours_format,
            "recette_mois_format": recette_mois_format,
            "recette_an_format": recette_an_format,
            "liste_recette": liste_recette,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_recettes', kwargs={'pk': self.kwargs['pk']})

class AddAutrarretView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_autarrets'
    model = Autrarret
    form_class = AutrarretForm
    template_name= "perfect/add_autarret.html"
    success_message = "Autre d'arrêt Ajouté avec succès ✓✓"
    error_message = "Erreur de saisie ✘✘ "
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        
        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        autarret_queryset = Autrarret.objects.filter(vehicule=vehicule)
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            
            if date_debut and date_fin:
                autarret_queryset = autarret_queryset.filter(
                    date_saisie__range=[date_debut, date_fin]
                )

        autarret_total = autarret_queryset.filter(date_saisie__month=date.today().month).count()

        autarret_jours = autarret_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        autarret_jours_format ='{:,}'.format(autarret_jours).replace('',' ')
        autarret_mois = autarret_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        autarret_mois_format ='{:,}'.format(autarret_mois).replace('',' ')
        autarret_an = autarret_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        autarret_an_format ='{:,}'.format(autarret_an).replace('',' ')
        
        liste_autarret = autarret_queryset.filter(date_saisie__month=date.today().month).order_by('-id')    

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "autarret_total": autarret_total,
            "autarret_jours_format": autarret_jours_format,
            "autarret_mois_format": autarret_mois_format,
            "autarret_an_format": autarret_an_format,
            "liste_autarret": liste_autarret,
            
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_autarrets', kwargs={'pk': self.kwargs['pk']})
    
class ListarretView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'liste_aut_arrets'
    model = Autrarret
    template_name = 'perfect/liste_arret.html'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        autarret_queryset = Autrarret.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            
        if categorie_filter:
            autarret_queryset = autarret_queryset.filter(vehicule__category__category=categorie_filter)
        if date_debut and date_fin:
            autarret_queryset = autarret_queryset.filter(date_saisie__range=[date_debut, date_fin])

        autarret_total = autarret_queryset.filter(date_saisie__month=date.today().month).count()
        
        autarret_jours = autarret_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        autarret_jours_format ='{:,}'.format(autarret_jours).replace('',' ')
        autarret_mois = autarret_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        autarret_mois_format ='{:,}'.format(autarret_mois).replace('',' ')
        autarret_an = autarret_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        autarret_an_format ='{:,}'.format(autarret_an).replace('',' ')

        liste_autarret = autarret_queryset
        context={
            'liste_autarret':liste_autarret,
            'autarret_total':autarret_total,
            'autarret_an_format':autarret_an_format,
            'autarret_mois_format':autarret_mois_format,
            'autarret_jours_format':autarret_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
            }
        return context 
     
class ListRecetView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'list_recet'
    model = Recette
    template_name = 'perfect/liste_recette.html'
    context_object = 'listrecet'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month

        recette_queryset = Recette.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            
        if categorie_filter:
            recette_queryset = recette_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            recette_queryset = recette_queryset.filter(date_saisie__range=[date_debut, date_fin])

        # ################################----Recettes----#############################
        recettes_jours = recette_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        recettes_jours_format ='{:,}'.format(recettes_jours).replace('',' ')
        recettes_mois = recette_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        recettes_mois_format ='{:,}'.format(recettes_mois).replace('',' ')
        recettes_an = recette_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        recettes_an_format ='{:,}'.format(recettes_an).replace('',' ')

        liste_rec = recette_queryset.filter(date_saisie__month=date.today().month)
        context={
            'liste_rec':liste_rec,
            
            'recettes_an_format':recettes_an_format,
            'recettes_mois_format':recettes_mois_format,
            'recettes_jours_format':recettes_jours_format,
            
            'dates':dates,
            'annees':annee,
            'form':form,
            }
        return context 
     
def delete_visite(request, pk):
    try:
        visites = get_object_or_404(VisiteTechnique, id=pk)
        visites.delete()
        messages.success(request, f"la recette du véhicule {visites.vehicule.immatriculation} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('list_visit')

def delete_recette(request, pk):
    try:
        recettres = get_object_or_404(Recette, id=pk)
        recettres.delete()
        messages.success(request, f"la recette du véhicule {recettres.vehicule.immatriculation} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('list_recet')

@require_POST
@login_required
def delete_selected_recettes(request):
    selected_ids = request.POST.getlist('selected_recettes')
    if selected_ids:
        recettes_to_delete = Recette.objects.filter(id__in=selected_ids)
        count = recettes_to_delete.count()
        recettes_to_delete.delete()
        messages.success(request, f"{count} recette(s) supprimée(s) avec succès.")
    else:
        messages.warning(request, "Aucune recette sélectionnée.")
    return redirect('list_recet')  # adapte si l’url de ListRecetView est différente

def delete_charg_var(request, pk):
    try:
        charg_variables = get_object_or_404(ChargeVariable, id=pk)
        charg_variables.delete()
        messages.success(request, f"la Charge variable du véhicule {charg_variables.vehicule.immatriculation} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('list_charg_var')

def delete_charg_fixe(request, pk):
    try:
        charg_fixes = get_object_or_404(ChargeFixe, id=pk)
        charg_fixes.delete()
        messages.success(request, f"la Charge fixe du véhicule {charg_fixes.vehicule.immatriculation} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('list_charg_fix')
    
class AddChargeFixView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'addcharg_fix'
    model = ChargeFixe
    form_class = ChargeFixForm
    template_name= "perfect/add_charg_fixe.html"
    success_message = 'Charge fixe Ajoutée avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘ "
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        chargfixe_queryset = ChargeFixe.objects.filter(vehicule=vehicule)
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            chargfixe_queryset = chargfixe_queryset.filter(date_saisie__range=[date_debut, date_fin])

        chargfixe_jours = chargfixe_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        chargfixe_jours_format ='{:,}'.format(chargfixe_jours).replace('',' ')
        chargfixe_mois = chargfixe_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        chargfixe_mois_format ='{:,}'.format(chargfixe_mois).replace('',' ')
        chargfixe_an = chargfixe_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        chargfixe_an_format ='{:,}'.format(chargfixe_an).replace('',' ')
        liste_chargfixe = chargfixe_queryset.filter(date_saisie__month=date.today().month)

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "chargfixe_jours_format": chargfixe_jours_format,
            "chargfixe_mois_format": chargfixe_mois_format,
            "chargfixe_an_format": chargfixe_an_format,
            "liste_chargfixe": liste_chargfixe,
            
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('addcharg_fix', kwargs={'pk': self.kwargs['pk']})
   
class ListChargeFixView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'list_charg_fix'
    model = ChargeFixe
    template_name = 'perfect/liste_charg_fix.html'
    context_object = 'list_charg_fix'
    form_class = DateFormMJR
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month

        chargefix_queryset = ChargeFixe.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if categorie_filter:
            chargefix_queryset = chargefix_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            chargefix_queryset = chargefix_queryset.filter(date_saisie__range=[date_debut, date_fin])
        # ################################----Recettes----#############################
        chargefix_jours = chargefix_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        chargefix_jours_format ='{:,}'.format(chargefix_jours).replace('',' ')
        chargefix_mois = chargefix_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        chargefix_mois_format ='{:,}'.format(chargefix_mois).replace('',' ')
        chargefix_an = chargefix_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        chargefix_an_format ='{:,}'.format(chargefix_an).replace('',' ')
        liste_chargefix = chargefix_queryset.filter(date_saisie__month=date.today().month)

        context={
            'liste_chargefix':liste_chargefix,
            'chargefix_an_format':chargefix_an_format,
            'chargefix_mois_format':chargefix_mois_format,
            'chargefix_jours_format':chargefix_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
            }
        return context 
     
class UpdateChargFixView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'upd_charg_fix'
    model = ChargeFixe
    form_class = UpdatChargeFixForm
    template_name = "perfect/chargfix_update.html" 
    success_message = 'Charge Fixe Modifiée avec succès✓✓'
    error_message = "Erreur de saisie✘✘ "
    success_url = reverse_lazy ('list_charg_fix')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_chargfix = ChargeFixe.objects.filter(date_saisie=date.today())
        chargfix=self.get_object()
        context = {
            'list_chargfix':list_chargfix,
            'forms':forms,
            'chargfix':chargfix,
        }
        return context 

class AddChargeVarView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'addcharg_var'
    model = ChargeVariable
    form_class = ChargeVarForm
    template_name= "perfect/add_charg_var.html"
    success_message = 'Charge variable Ajoutée avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        chargvar_queryset = ChargeVariable.objects.filter(vehicule=vehicule)
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  
                # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none()
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            chargvar_queryset = chargvar_queryset.filter(date_saisie__range=[date_debut, date_fin])

        chargvar_jours = chargvar_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        chargvar_jours_format ='{:,}'.format(chargvar_jours).replace('',' ')
        chargvar_mois = chargvar_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        chargvar_mois_format ='{:,}'.format(chargvar_mois).replace('',' ')
        chargvar_an = chargvar_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        chargvar_an_format ='{:,}'.format(chargvar_an).replace('',' ')
        liste_chargvar = chargvar_queryset.filter(date_saisie__month=date.today().month)

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            'chargvar_jours_format': chargvar_jours_format,
            'chargvar_mois_format': chargvar_mois_format,
            'chargvar_an_format': chargvar_an_format,
            'liste_chargvar': liste_chargvar,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('addcharg_var', kwargs={'pk': self.kwargs['pk']})

class ListChargeVarView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'list_charg_var'
    model = ChargeVariable
    template_name = 'perfect/liste_charg_var.html'
    context_object = 'list_charg_var'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month

        chargevar_queryset = ChargeVariable.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if categorie_filter:
            chargevar_queryset = chargevar_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            chargevar_queryset = chargevar_queryset.filter(date_saisie__range=[date_debut, date_fin])
        # ################################----Recettes----#############################
        chargevar_jours = chargevar_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        chargevar_jours_format ='{:,}'.format(chargevar_jours).replace('',' ')
        chargevar_mois = chargevar_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        chargevar_mois_format ='{:,}'.format(chargevar_mois).replace('',' ')
        chargevar_an = chargevar_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        chargevar_an_format ='{:,}'.format(chargevar_an).replace('',' ')
        liste_chargevar = chargevar_queryset.filter(date_saisie__month=date.today().month)

        context={
            'liste_chargevar':liste_chargevar,
            'chargevar_an_format':chargevar_an_format,
            'chargevar_mois_format':chargevar_mois_format,
            'chargevar_jours_format':chargevar_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
            }
        return context

class AddChargeAdminisView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_chargadminist'
    model = ChargeAdminis
    form_class = ChargeAdminisForm
    template_name = 'perfect/add_charg_admin.html'
    success_message = 'Charge administrative enregistrée avec succès✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('add_chargadminist')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        annee_en_cours =date.today().year
        today = date.today()
        mois_en_cours =date.today().month
        libelle_mois_en_cours = calendar.month_name[mois_en_cours]
         
        form_admin = DateForm(self.request.GET)
        if form_admin.is_valid():
            date_debut = form_admin.cleaned_data['date_debut']       
            date_fin = form_admin.cleaned_data['date_fin']
            charg_administ = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
            
            charg_adm_jour = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_jour_format ='{:,}'.format(charg_adm_jour).replace('',' ')
            charg_adm_mois = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_mois_format ='{:,}'.format(charg_adm_mois).replace('',' ')
            charg_adm_annuel = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_annuel_format ='{:,}'.format(charg_adm_annuel).replace('',' ')
            
            charg_adm_result = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(Sum('montant'))['montant__sum'] or 0
            
            charg_admin_data = ChargeAdminis.objects.filter(date_saisie__range=[date_debut, date_fin])
            chargadmin_mois_data = {month: 0 for month in range(1, 13)}
            for commande in charg_admin_data:
                chargadmin_mois_data[commande.date_saisie.month] += commande.montant
            chargadmin_mois_data = [chargadmin_mois_data[month] for month in range(1, 13)]
            label = [calendar.month_name[month][:1] for month in range(1, 13)]
            
            total_recettes = Recette.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
            total_piece= Piece.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
            total_charg_var = ChargeVariable.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            total_charge_format ='{:,}'.format(total_charg).replace('',' ')
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            
            if total_recettes == 0:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
            resultat = marge_brute-charg_adm_mois
            resultat_format ='{:,}'.format(resultat).replace('',' ')
        else:
            charg_administ = ChargeAdminis.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            charg_adm_jour = ChargeAdminis.objects.filter(date_saisie=date.today()).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_jour_format ='{:,}'.format(charg_adm_jour).replace('',' ')
            charg_adm_mois = ChargeAdminis.objects.filter(date_saisie__month=date.today().month).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_mois_format ='{:,}'.format(charg_adm_mois).replace('',' ')
            charg_adm_annuel = ChargeAdminis.objects.filter(date_saisie__year=date.today().year).aggregate(Sum('montant'))['montant__sum'] or 0
            charg_adm_annuel_format ='{:,}'.format(charg_adm_annuel).replace('',' ')
            
            charg_adm_result = ChargeAdminis.objects.filter(date_saisie=date.today()).aggregate(Sum('montant'))['montant__sum'] or 0
            
            charg_admin_data = ChargeAdminis.objects.filter(date_saisie__year=date.today().year)
            chargadmin_mois_data = {month: 0 for month in range(1, 13)}
            for commande in charg_admin_data:
                chargadmin_mois_data[commande.date_saisie.month] += commande.montant
            chargadmin_mois_data = [chargadmin_mois_data[month] for month in range(1, 13)]
            label = [calendar.month_name[month][:1] for month in range(1, 13)]
            
            total_recettes = Recette.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
            total_recette_format ='{:,}'.format(total_recettes).replace('',' ')
            total_piece= Piece.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_format ='{:,}'.format(total_piece).replace('',' ')
            ################################----Pieces echanges----#############################
            total_piec_echange= PiecEchange.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            total_piece_echang_format ='{:,}'.format(total_piec_echange).replace('',' ')
            ################################----Charges----#############################
            total_charg_fix = ChargeFixe.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargfix_format ='{:,}'.format(total_charg_fix).replace('',' ')
            total_charg_var = ChargeVariable.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            total_chargvar_format ='{:,}'.format(total_charg_var).replace('',' ')
            ################################----Charge Totale----#############################
            total_charg = total_charg_fix + total_charg_var
            total_charge_format ='{:,}'.format(total_charg).replace('',' ')
            ################################----Marge de contribution----#############################
            # marge_contribution = total_recettes - total_charg
            marge_contribution = total_recettes - total_charg_var
            
            if total_recettes == 0:
                taux_marge = 0
            else:
                taux_marge = (marge_contribution*100/(total_recettes))
            taux_marge_format ='{:.2f}'.format(taux_marge)
            ################################----Marge brute----#############################
            marge_brute = total_recettes - total_charg
            marge_brute_format ='{:,}'.format(marge_brute).replace('',' ')
            resultat = marge_brute-charg_adm_mois
            resultat_format ='{:,}'.format(resultat).replace('',' ')
            
        context={
            'total_recette_format':total_recette_format,
            
            'list_charge_adminis':charg_administ,
            'taux_marge_format':taux_marge_format,
            'total_chargfix_format':total_chargfix_format,
            'total_chargvar_format':total_chargvar_format,
            'total_piece_format':total_piece_format,
            'total_piece_echang_format':total_piece_echang_format,
            'marge_brute_format':marge_brute_format,
            'total_charge_format':total_charge_format,
            
            'labels':label,
            'forms':forms,
            'form':form_admin,
            'resultat_format':resultat_format,
            
            'dates':today,
            'mois':libelle_mois_en_cours,
            'annee':annee_en_cours,
            
            'charg_adm_jour_format':charg_adm_jour_format,
            'charg_adm_mois_format':charg_adm_mois_format,
            'charg_adm_annuel_format':charg_adm_annuel_format,
            
            'charg_adm_result':charg_adm_result,
            'chargadmin_data':chargadmin_mois_data,
        }  
        return context   
    
def delete_chargadmin(request, pk):
    try:
        chargadmin = get_object_or_404(ChargeAdminis, id=pk)
        chargadmin.delete()
        messages.success(request, f"la charge administrative {chargadmin.Num_fact}-{chargadmin.date_saisie} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_chargadminist')

#--------------/-/---------------@-----------------/-/--------------Garage---------------/-/--------------@----------------/-/------------#

class AddCartStationView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_station'
    model = Stationnement
    form_class = CartStationForm
    template_name= "perfect/add_station.html"
    success_message = 'Carte de Stationnement enregistrée avec succès✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        station_queryset = Stationnement.objects.filter(vehicule=vehicule)

        
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None

        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()
        
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            station_queryset = station_queryset.filter(date_saisie__range=[date_debut, date_fin])

        station_jours = station_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        station_jours_format ='{:,}'.format(station_jours).replace('',' ')
        station_mois = station_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        station_mois_format ='{:,}'.format(station_mois).replace('',' ')
        station_an = station_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        station_an_format ='{:,}'.format(station_an).replace('',' ')
        liste_station = station_queryset.filter(date_saisie__month=date.today().month)

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            'station_jours_format': station_jours_format,
            'station_mois_format': station_mois_format,
            'station_an_format': station_an_format,
            'liste_station': liste_station,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_station', kwargs={'pk': self.kwargs['pk']})

class ListCartStationView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'liste_station'
    model = Stationnement
    template_name = 'perfect/liste_station.html'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month

        station_queryset = Stationnement.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if categorie_filter:
            station_queryset = station_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            station_queryset = station_queryset.filter(date_saisie__range=[date_debut, date_fin])
        # ################################----Recettes----#############################
        station_jours = station_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        station_jours_format ='{:,}'.format(station_jours).replace('',' ')
        station_mois = station_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        station_mois_format ='{:,}'.format(station_mois).replace('',' ')
        station_an = station_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        station_an_format ='{:,}'.format(station_an).replace('',' ')
        liste_station = station_queryset

        context={
            'liste_station':liste_station,
            'station_an_format':station_an_format,
            'station_mois_format':station_mois_format,
            'station_jours_format':station_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
        }
        return context


class AddPatenteView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_patente'
    model = Patente
    form_class = PatenteForm
    template_name= "perfect/add_patente.html"
    success_message = 'Patente enregistrée avec succès✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        patent_queryset = Patente.objects.filter(vehicule=vehicule)

        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None

        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()
        
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            patent_queryset = patent_queryset.filter(date_saisie__range=[date_debut, date_fin])

        patente_jours = patent_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        patente_jours_format ='{:,}'.format(patente_jours).replace('',' ')
        patente_mois = patent_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        patente_mois_format ='{:,}'.format(patente_mois).replace('',' ')
        patente_an = patent_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        patente_an_format ='{:,}'.format(patente_an).replace('',' ')
        liste_patente = patent_queryset.filter(date_saisie__month=date.today().month)

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            'patente_jours_format': patente_jours_format,
            'patente_mois_format': patente_mois_format,
            'patente_an_format': patente_an_format,
            'liste_patente': liste_patente,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_patente', kwargs={'pk': self.kwargs['pk']})

def delete_patente(request, pk):
    try:
        patentes = get_object_or_404(Patente, id=pk)
        vehicule_pk = patentes.vehicule.id 
        patentes.delete()
        messages.success(request, f"La patente du véhicule {patentes.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_patente', pk=vehicule_pk)

def delete_stat(request, pk):
    try:
        stat = get_object_or_404(Stationnement, id=pk)
        vehicule_pk = stat.vehicule.id 
        stat.delete()
        messages.success(request, f"Le carte de stationnement du véhicule {stat.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_station', pk=vehicule_pk)

def delete_autarret(request, pk):
    try:
        autar = get_object_or_404(Autrarret, id=pk)
        vehicule_pk = autar.vehicule.id 
        autar.delete()
        messages.success(request, f"L'arrêt du véhicule {autar.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_autarrets', pk=vehicule_pk)

class ListPatenteView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'liste_patente'
    model = Patente
    template_name = 'perfect/liste_patente.html'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        patente_queryset = Patente.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
        if categorie_filter:
            patente_queryset = patente_queryset.filter(vehicule__category__category=categorie_filter)
        if date_debut and date_fin:
            patente_queryset = patente_queryset.filter(date_saisie__range=[date_debut, date_fin])
        patente_jours = patente_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        patente_jours_format ='{:,}'.format(patente_jours).replace('',' ')
        patente_mois = patente_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        patente_mois_format ='{:,}'.format(patente_mois).replace('',' ')
        patente_an = patente_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        patente_an_format ='{:,}'.format(patente_an).replace('',' ')
        liste_patente = patente_queryset

        context={
            'liste_patente':liste_patente,
            'patente_an_format':patente_an_format,
            'patente_mois_format':patente_mois_format,
            'patente_jours_format':patente_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
        }
        return context

class AddVignetteView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_vignet'
    model = Vignette
    form_class = VignetteForm
    template_name= "perfect/add_vignette.html"
    success_message = 'Vignette enregistrée avec succès✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        vignette_queryset = Assurance.objects.filter(vehicule=vehicule)

        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None

        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
        
        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            vignette_queryset = vignette_queryset.filter(date_saisie__range=[date_debut, date_fin])

        vignette_jours = vignette_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        vignette_jours_format ='{:,}'.format(vignette_jours).replace('',' ')
        vignette_mois = vignette_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        vignette_mois_format ='{:,}'.format(vignette_mois).replace('',' ')
        vignette_an = vignette_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        vignette_an_format ='{:,}'.format(vignette_an).replace('',' ')
        liste_vignette = vignette_queryset.filter(date_saisie__month=date.today().month)

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            'vignette_jours_format':vignette_jours_format,
            'vignette_mois_format':vignette_mois_format,
            'vignette_an_format':vignette_an_format,
            'liste_vignette':liste_vignette,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }     
        return context  
    def get_success_url(self):
        return reverse('add_vignet', kwargs={'pk': self.kwargs['pk']})

class ListVignetteView(LoginRequiredMixin, CustomPermissionRequiredMixin,ListView):
    login_url = 'login'
    permission_url = 'liste_vignette'
    model = Vignette
    template_name = 'perfect/liste_vignette.html'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month

        vignet_queryset = Vignette.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if categorie_filter:
            vignet_queryset = vignet_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            vignet_queryset = vignet_queryset.filter(date_saisie__range=[date_debut, date_fin])
        # ################################----Recettes----#############################
        vignet_jours = vignet_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        vignet_jours_format ='{:,}'.format(vignet_jours).replace('',' ')
        vignet_mois = vignet_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        vignet_mois_format ='{:,}'.format(vignet_mois).replace('',' ')
        vignet_an = vignet_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        vignet_an_format ='{:,}'.format(vignet_an).replace('',' ')
        liste_vignet = vignet_queryset

        context={
            'liste_vignet':liste_vignet,
            'vignet_an_format':vignet_an_format,
            'vignet_mois_format':vignet_mois_format,
            'vignet_jours_format':vignet_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
        }
        return context

class AddVisitView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_visit'
    model = VisiteTechnique
    form_class = VisiteTechniqueForm
    template_name= "perfect/add_visite.html"
    success_message = 'Visite Ajoutée avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘ "
    # success_url = reverse_lazy('journal_compta')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        visitech_queryset = VisiteTechnique.objects.filter(vehicule=vehicule)
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  
                # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            visitech_queryset = visitech_queryset.filter(date_saisie__range=[date_debut, date_fin])

        visitech_jours = visitech_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        visitech_jours_format ='{:,}'.format(visitech_jours).replace('',' ')
        visitech_mois = visitech_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        visitech_mois_format ='{:,}'.format(visitech_mois).replace('',' ')
        visitech_an = visitech_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        visitech_an_format ='{:,}'.format(visitech_an).replace('',' ')
        liste_visitech = visitech_queryset
        
        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            'liste_visitech':liste_visitech,
            'visitech_an_format':visitech_an_format,
            'visitech_mois_format':visitech_mois_format,
            'visitech_jours_format':visitech_jours_format,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_visit', kwargs={'pk': self.kwargs['pk']})

class ListVisitView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'list_visit'
    model = VisiteTechnique
    template_name = 'perfect/liste_visites.html'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month

        visitech_queryset = VisiteTechnique.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if categorie_filter:
            visitech_queryset = visitech_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            visitech_queryset = visitech_queryset.filter(date_saisie__range=[date_debut, date_fin])
        # ################################----Recettes----#############################
        visitech_jours = visitech_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        visitech_jours_format ='{:,}'.format(visitech_jours).replace('',' ')
        visitech_mois = visitech_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        visitech_mois_format ='{:,}'.format(visitech_mois).replace('',' ')
        visitech_an = visitech_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        visitech_an_format ='{:,}'.format(visitech_an).replace('',' ')
        liste_visitech = visitech_queryset

        context={
            'liste_visitech':liste_visitech,
            'visitech_an_format':visitech_an_format,
            'visitech_mois_format':visitech_mois_format,
            'visitech_jours_format':visitech_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
        }
        return context

class AddAssuranceView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_assurance'
    model = Assurance
    form_class = AssuranceForm
    template_name= "perfect/add_assurance.html"
    success_message = 'Assurance enregistré avec succès✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        assurance_queryset = Assurance.objects.filter(vehicule=vehicule)

        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None

        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()
        
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            assurance_queryset = assurance_queryset.filter(date_saisie__range=[date_debut, date_fin])

        assurance_jours = assurance_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        assurance_jours_format ='{:,}'.format(assurance_jours).replace('',' ')
        assurance_mois = assurance_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        assurance_mois_format ='{:,}'.format(assurance_mois).replace('',' ')
        assurance_an = assurance_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        assurance_an_format ='{:,}'.format(assurance_an).replace('',' ')
        liste_recette = assurance_queryset.filter(date_saisie__month=date.today().month)

        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "assurance_an_format": assurance_an_format,
            "assurance_mois_format": assurance_mois_format,
            "assurance_jours_format": assurance_jours_format,
            "liste_recette": liste_recette,
            
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }    
        return context  
    def get_success_url(self):
        return reverse('add_assurance', kwargs={'pk': self.kwargs['pk']})

class ListAssuranceView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'liste_assurance'
    model = Assurance
    template_name = 'perfect/liste_assurance.html'
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month

        assur_queryset = Assurance.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if categorie_filter:
            assur_queryset = assur_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            assur_queryset = assur_queryset.filter(date_saisie__range=[date_debut, date_fin])
        # ################################----Recettes----#############################
        assur_jours = assur_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        assur_jours_format ='{:,}'.format(assur_jours).replace('',' ')
        assur_mois = assur_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        assur_mois_format ='{:,}'.format(assur_mois).replace('',' ')
        assur_an = assur_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        assur_an_format ='{:,}'.format(assur_an).replace('',' ')
        liste_assur = assur_queryset

        context={
            'liste_assur':liste_assur,
            'assur_an_format':assur_an_format,
            'assur_mois_format':assur_mois_format,
            'assur_jours_format':assur_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
        }
        return context

class AddReparationView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_reparation'
    model = Reparation
    form_class = ReparationForm
    template_name= "perfect/add_reparation.html"
    success_message = 'Réparation enregistrée avec succès✓✓'
    error_message = "Erreur de saisie ✘✘"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        # now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        form = DateFormRepar(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        if self.request.POST:
            piece_formset = PieceFormSet(self.request.POST, instance=self.object)
        else:
            piece_formset = PieceFormSet(instance=self.object)
        forms = self.get_form()
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        reparat_queryset = Reparation.objects.filter(vehicule=vehicule)
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            motif_filter = self.request.GET.get('motif') 
            
            if date_debut and date_fin:
                reparat_queryset = reparat_queryset.filter(
                    date_saisie__range=[date_debut, date_fin]
                )
            if motif_filter:
                reparat_queryset = reparat_queryset.filter(motif=motif_filter)

        # Calculs
        reparat_total = reparat_queryset.filter(date_saisie__month=date.today().month).count()
        reparat_jours = reparat_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        reparat_jours_format ='{:,}'.format(reparat_jours).replace('',' ')
        reparat_mois = reparat_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        reparat_mois_format ='{:,}'.format(reparat_mois).replace('',' ')
        reparat_an = reparat_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        reparat_an_format ='{:,}'.format(reparat_an).replace('',' ')
        
        liste_reparat = reparat_queryset.order_by('-id')
        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "piece_formset": piece_formset,
            "liste_reparat": liste_reparat,
            
            "reparat_total": reparat_total,
            "reparat_jours_format": reparat_jours_format,
            "reparat_mois_format": reparat_mois_format,
            "reparat_an_format": reparat_an_format,

            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        piece_formset = context['piece_formset']
        # Associer véhicule et auteur AVANT la validation finale
        form.instance.vehicule_id = self.kwargs['pk']
        form.instance.auteur = self.request.user  

        if form.is_valid() and piece_formset.is_valid():
            self.object = form.save(commit=False)
            total_pieces = 0
            for piece_form in piece_formset:
                piece = piece_form.save(commit=False)
                if piece.libelle:  # éviter les formulaires vides
                    piece.auteur = self.request.user  
                    piece.reparation = self.object
                    total_pieces += (piece.montant or 0) * (piece.quantite or 1)

            # calcul du montant total
            prestation = form.cleaned_data.get("prestation", 0)
            self.object.montant = total_pieces + prestation
            self.object.save()
            # maintenant on rattache les pièces à la réparation
            piece_formset.instance = self.object
            piece_formset.save()

            messages.success(self.request, self.success_message)
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)
    def form_invalid(self, form):
        context = self.get_context_data()
        piece_formset = context['piece_formset']
        print("=== ERREURS REPARATION ===")
        print(form.errors)
        print("=== ERREURS PIECES ===")
        print(piece_formset.errors)
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)
    def get_success_url(self):
        return reverse('add_reparation', kwargs={'pk': self.kwargs['pk']})

def delete_reparation(request, pk):
    try:
        reparation = get_object_or_404(Reparation, id=pk)
        vehicule_pk = reparation.vehicule.id 
        reparation.delete()
        messages.success(request, f"La réparation du véhicule {reparation.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_reparation', pk=vehicule_pk)

def delete_assurance(request, pk):
    try:
        assur = get_object_or_404(Assurance, id=pk)
        vehicule_pk = assur.vehicule.id 
        assur.delete()
        messages.success(request, f"L'assurance du véhicule {assur.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_assurance', pk=vehicule_pk)

def delete_vignette(request, pk):
    try:
        vig = get_object_or_404(Vignette, id=pk)
        vehicule_pk = vig.vehicule.id 
        vig.delete()
        messages.success(request, f"La vignette du véhicule {vig.vehicule.immatriculation} a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_vignet', pk=vehicule_pk)

class AddPiecEchangeView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_piechange'
    model = PiecEchange
    form_class = PiecEchangeForm
    template_name= "perfect/add_piecechange.html"
    success_message = 'Pièces enregistrées avec succès✓✓'
    error_message = "Erreur de saisie✘✘"
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.success(self.request,self.error_message)
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        piechange_queryset = PiecEchange.objects.filter(vehicule=vehicule)
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None

        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()
        
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            piechange_queryset = piechange_queryset.filter(date_saisie__range=[date_debut, date_fin])

        piechange_jours = piechange_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        piechange_jours_format ='{:,}'.format(piechange_jours).replace('',' ')
        piechange_mois = piechange_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        piechange_mois_format ='{:,}'.format(piechange_mois).replace('',' ')
        piechange_an = piechange_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        piechange_an_format ='{:,}'.format(piechange_an).replace('',' ')
        liste_piechange = piechange_queryset.filter(date_saisie__month=date.today().month)
        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            "piechange_jours_format": piechange_jours_format,
            "piechange_mois_format": piechange_mois_format,
            "piechange_an_format": piechange_an_format,
            "liste_piechange": liste_piechange,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }      
        return context  
    def get_success_url(self):
        return reverse('add_piechange', kwargs={'pk': self.kwargs['pk']})
    
def delete_piecechange(request, pk):
    try:
        piecechange = get_object_or_404(PiecEchange, id=pk)
        vehicule_pk = piecechange.vehicule.id 
        piecechange.delete()
        messages.success(request, f"la pièce changé du {piecechange.vehicule.immatriculation}- saisie le: {piecechange.date} a été supprimés avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    return redirect('add_piechange', pk=vehicule_pk)

class DetailReparatView(LoginRequiredMixin, CustomPermissionRequiredMixin, DetailView):
    login_url = 'login'
    permission_url = 'detail_reparat'
    model = Reparation
    template_name = 'perfect/detail_reparat.html'
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def calculate_effective_hours(self, start, end):
        total_seconds = 0
        current = start
        while current < end:
            next_hour = (current + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            if next_hour > end:
                next_hour = end

            if time(5, 0) <= current.time() < time(22, 0):
                total_seconds += (next_hour - current).total_seconds()
            
            current = next_hour
        return total_seconds / 3600
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        mois_en_cours =date.today().month
        reparation = get_object_or_404(Reparation, pk=self.kwargs['pk'])
        list_piece= reparation.pieces.all()

        # reparations  = self.get_object()
        vehicule = reparation.vehicule
        user = self.request.user
        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")
            
        date_entree = reparation.date_entree
        date_sortie = reparation.date_sortie
        duree_effective_heures = self.calculate_effective_hours(date_entree, date_sortie)

        if vehicule.category.category == "TAXI":
            perte_par_30min = 550
            recette_categorie = 20000
        elif vehicule.category.category == "VTC":
            perte_par_30min = 600
            recette_categorie = 22000
        else:
            perte_par_30min = 0
            recette_categorie = 0

        perte = (duree_effective_heures * 2) * perte_par_30min
        recette_nette = recette_categorie - perte
        #-------------------------------------------------------------------------------------------------------------------------------
        # list_reparation = Reparation.objects.filter(vehicule=vehicule)
        ################################----Pieces----#############################
        total_piece= Piece.objects.filter(reparation = reparation,).aggregate(somme=Sum('montant'))['somme'] or 0
        
        
        context={
            'reparation':reparation,
            'duree_effective_heures':duree_effective_heures,
            'perte':perte,
            'recette_nette':recette_nette,
            'vehicules':vehicules,
            'total_piece':total_piece,
            'list_piece':list_piece,
            # 'list_reparation':list_reparation,
            'dates':dates
        }
        return context

class ListPiechangeView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'list_piechange'
    model = PiecEchange
    template_name = 'perfect/liste_piechange.html'
    ordering = ['date_saisie']
    timeout_minutes = 500
    form_class = DateFormMJR
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        piechange_queryset = PiecEchange.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
        if categorie_filter:
            piechange_queryset = piechange_queryset.filter(vehicule__category__category=categorie_filter)
        if date_debut and date_fin:
            piechange_queryset = piechange_queryset.filter(date_saisie__range=[date_debut, date_fin])
        piechange_jours = piechange_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        piechange_jours_format ='{:,}'.format(piechange_jours).replace('',' ')
        piechange_mois = piechange_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        piechange_mois_format ='{:,}'.format(piechange_mois).replace('',' ')
        piechange_an = piechange_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        piechange_an_format ='{:,}'.format(piechange_an).replace('',' ')
        liste_piechange = piechange_queryset

        context={
            'liste_piechange':liste_piechange,
            'piechange_an_format':piechange_an_format,
            'piechange_mois_format':piechange_mois_format,
            'piechange_jours_format':piechange_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
        }
        return context

class ListReparationView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'list_repa'
    model = Reparation
    template_name = 'perfect/liste_reparations.html'
    ordering = ['date_saisie']
    context_object = 'listereparation'
    timeout_minutes = 300
    form_class = DateFormListRepar
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    # Reparation
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        mois = date.today().month
        reparat_queryset = Reparation.objects.all()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            categorie_filter = form.cleaned_data.get('categorie')
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')
            motif_filter = form.cleaned_data.get('motif')

        if categorie_filter:
            reparat_queryset = reparat_queryset.filter(vehicule__category__category=categorie_filter)

        if date_debut and date_fin:
            reparat_queryset = reparat_queryset.filter(date_saisie__range=[date_debut, date_fin])

        if motif_filter:
            reparat_queryset = reparat_queryset.filter(motif=motif_filter)

        reparat_total = reparat_queryset.filter(date_saisie__month=date.today().month).count()
        reparat_jours = reparat_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        reparat_jours_format ='{:,}'.format(reparat_jours).replace('',' ')
        reparat_mois = reparat_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        reparat_mois_format ='{:,}'.format(reparat_mois).replace('',' ')
        reparat_an = reparat_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        reparat_an_format ='{:,}'.format(reparat_an).replace('',' ')
        liste_reparat = reparat_queryset

        context={
            'liste_reparat':liste_reparat,
            'reparat_total':reparat_total,
            'reparat_an_format':reparat_an_format,
            'reparat_mois_format':reparat_mois_format,
            'reparat_jours_format':reparat_jours_format,
            'dates':dates,
            'annees':annee,
            'form':form,
        }
        return context

 
         
class AddEntretienView(LoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    login_url = 'login'
    permission_url = 'add_entretien'
    model = Entretien
    form_class = EntretienForm
    template_name= "perfect/add_entre.html"
    success_message = 'Entretien Ajouté avec succès ✓✓'
    error_message = "Erreur de saisie ✘✘ "
    # success_url = reverse_lazy('journal_compta')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        form.instance.vehicule_id = self.kwargs['pk']
        messages.success(self.request, self.success_message)
        return super().form_valid(form)  
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = date.today()
        annee = date.today().year
        now = datetime.now()
        mois_en_cours = date.today().month
        libelle_mois = calendar.month_name[mois_en_cours]
        vehicule = get_object_or_404(Vehicule, pk=self.kwargs['pk'])
        entret_queryset = Entretien.objects.filter(vehicule=vehicule)
        form = DateForm(self.request.GET)
        forms = self.get_form()
        user = self.request.user
        date_debut = date_fin = None

        if user.user_type == "4":
            try:
                gerant = user.gerants.get()
                if gerant.gerant_voiture == "VTC":
                    vehicules = Vehicule.objects.filter(category__category="VTC")
                else:
                    vehicules = Vehicule.objects.filter(category__category="TAXI")
            except Gerant.DoesNotExist:
                vehicules = Vehicule.objects.none()  
                # No vehicles if no Gerant linked
        elif user:
            try:
                vehicules = Vehicule.objects.all()
            except:
                vehicules = Vehicule.objects.none() 
        else:
            print("*****ALL*******")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:  
            vehicules = search_vehicules(vehicules, search_query)
        else:
            vehicules = Vehicule.objects.none()

        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut')
            date_fin = form.cleaned_data.get('date_fin')

        if date_debut and date_fin:
            entret_queryset = entret_queryset.filter(date_saisie__range=[date_debut, date_fin])

        entret_jours = entret_queryset.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 1
        entret_jours_format ='{:,}'.format(entret_jours).replace('',' ')
        entret_mois = entret_queryset.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 1
        entret_mois_format ='{:,}'.format(entret_mois).replace('',' ')
        entret_an = entret_queryset.filter(date_saisie__year=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 1
        entret_an_format ='{:,}'.format(entret_an).replace('',' ')
        liste_entret = entret_queryset.filter(date_saisie__month=date.today().month)
        
        context = {
            "vehicules": vehicules,
            "vehicule": vehicule,
            'entret_jours_format': entret_jours_format,
            'entret_mois_format': entret_mois_format,
            'entret_an_format': entret_an_format,
            'liste_entret': liste_entret,
            'dates': dates,
            'mois': libelle_mois,
            'annee': annee,
            'form': form,
            'forms': forms,
        }   
        return context  
    def get_success_url(self):
        return reverse('add_entretien', kwargs={'pk': self.kwargs['pk']})

class ListEntretienView(LoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    login_url = 'login'
    permission_url = 'list_entretien'
    model = Entretien
    template_name = 'perfect/liste_entretien.html'
    ordering = ['date_saisie']
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates=date.today()
        annee=date.today().year
        mois=date.today().month
        libelle_mois= calendar.month_name[mois]
        forms = DateForm(self.request.GET)
        if forms.is_valid():
            date_debut = forms.cleaned_data['date_debut'] 
            date_fin = forms.cleaned_data['date_fin']
            
            ent_all = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour = Entretien.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_vtc = Entretien.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_taxi = Entretien.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_all = Entretien.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_an_fil_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_an_fil_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI', date_saisie__range=[date_debut, date_fin]).aggregate(somme=Sum('montant'))['somme'] or 0

            list_ent = Entretien.objects.filter(date_saisie__range=[date_debut, date_fin]).order_by('-id')
        else:
            ent_all = Entretien.objects.filter(date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_all_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour = Entretien.objects.filter(date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_vtc = Entretien.objects.filter(vehicule__category__category='VTC',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_jour_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI',date_saisie=date.today()).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_taxi = Entretien.objects.filter(vehicule__category__category='TAXI',date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_mois_all = Entretien.objects.filter(date_saisie__month=date.today().month).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_an_fil_vtc = Entretien.objects.filter(vehicule__category__category = 'VTC', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            ent_an_fil_taxi = Entretien.objects.filter(vehicule__category__category = 'TAXI', date_saisie__month=date.today().year).aggregate(somme=Sum('montant'))['somme'] or 0
            list_ent = Entretien.objects.filter(date_saisie__month=date.today().month).order_by('-id')
            
        context={
            'list_ent':list_ent,
            'ent_jour':ent_jour,
            'ent_jour_vtc':ent_jour_vtc,
            'ent_mois_vtc':ent_mois_vtc,
            
            'ent_mois_taxi':ent_mois_taxi,
            'ent_jour_taxi':ent_jour_taxi,
            
            'ent_all':ent_all,
            
            'dates':dates,
            'libelles_mois':libelle_mois,
            'annees':annee,
            
            'ent_mois_all':ent_mois_all,
            
            'ent_all_vtc':ent_all_vtc,
            'ent_all_taxi':ent_all_taxi,
            'form':forms,
            'ent_an_fil_vtc' : ent_an_fil_vtc,
            'ent_an_fil_taxi': ent_an_fil_taxi,
            }
        return context 
    
class UpdatPatenteView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_patente'
    model = Patente
    form_class = UpdatPatenteForm
    template_name= "perfect/pat_update.html"
    success_message = 'Patente modifiée avec succès✓✓'
    error_message = "Erreur de saisie✘✘ "
    success_url = reverse_lazy('liste_patente')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_patentes = Patente.objects.all()
        # list_patentes = Patente.objects.filter(date_saisie=date.today())
        patents=self.get_object()
        context = {
            'list_patentes':list_patentes,
            'forms':forms,
            'patents':patents,
        }
        return context
    
class UpdateAssuranceView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_assurance'
    model = Assurance
    form_class = UpdatAssuranceForm
    template_name = "perfect/assurance_update.html" 
    success_message = 'Assurance Modifiée avec succès✓✓'
    error_message = "Erreur de saisie✘✘"
    success_url = reverse_lazy ('liste_assurance')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_assurance = Assurance.objects.all()
        # list_patentes = Patente.objects.filter(date_saisie=date.today())
        assurance=self.get_object()
        context = {
            'list_assurance':list_assurance,
            'forms':forms,
            'assurance':assurance,
        }
        return context 
 
class UpdatEntretienView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_entretien'
    model = Entretien
    form_class = UpdatEntretienForm
    template_name = "perfect/update_entretien.html"
    context_object = 'listvehi'  
    success_message = 'Entretien Modifiée avec succès✓✓'
    error_message = "Erreur de saisie✘✘ "
    success_url = reverse_lazy ('list_entretien')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context 

class UpdateVisiteView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_visit'
    model = VisiteTechnique
    form_class = VisiteTechniqueForm
    template_name = "perfect/visite_update.html" 
    success_message = 'Visite Techniques Modifiée avec succès✓✓'
    error_message = "Erreur de saisie✘✘"
    success_url = reverse_lazy ('list_visit')
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_visite = VisiteTechnique.objects.all()
        visite=self.get_object()
        context = {
            'list_visite':list_visite,
            'forms':forms,
            'visite':visite,
        }
        return context 
    
class UpdatVignetteView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_vignet'
    model = Vignette
    form_class = UpdatVignetteForm
    template_name = "perfect/vignette_update.html"
    success_message = 'Vignette modifiée avec succès✓✓'
    success_url = reverse_lazy ('liste_vignette')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_vignet = Vignette.objects.all()
        vignet=self.get_object()
        context = {
            'list_vignet':list_vignet,
            'forms':forms,
            'vignet':vignet,
        }
        return context

class UpdatCartStationView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_station'
    model = Stationnement
    form_class = UpdatCartStationForm
    template_name= "perfect/station_update.html"
    success_message = 'Modification de carte de station éffectuée avec succès✓✓'
    success_url = reverse_lazy ('liste_station')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_station = Stationnement.objects.all()
        station=self.get_object()
        context = {
            'list_station':list_station,
            'forms':forms,
            'station':station,
        }
        return context

class UpdateChargeAdminView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_charg_administ'
    model = ChargeAdminis
    form_class = updatChargeAdminisForm
    template_name = "perfect/update_chargadmin.html"
    success_message = 'Charge Administrative Modifiée avec succès✓✓'
    success_url = reverse_lazy('add_chargadminist')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_chargadmin = ChargeAdminis.objects.filter(date_saisie=date.today())
        chargadmin=self.get_object()
        context = {
            'list_chargadmin':list_chargadmin,
            'forms':forms,
            'chargadmin':chargadmin,
        }
        return context 
   
class UpdateChargeVarView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_charg_var'
    model = ChargeVariable
    form_class = updatChargeVarForm
    template_name = "perfect/chargvar_update.html"
    context_object = 'listvehi'  
    success_message = 'Charge Variable Modifiée avec succès✓✓'
    error_message = "Erreur de saisie✘✘"
    success_url = reverse_lazy ('list_charg_var')
    timeout_minutes = 500
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_chargvar = ChargeVariable.objects.filter(date_saisie=date.today())
        chargvar=self.get_object()
        context = {
            'list_chargvar':list_chargvar,
            'forms':forms,
            'chargvar':chargvar,
        }
        return context 

class UpdatEncaissementView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_encaisse'
    model = Encaissement
    form_class = UpdatEncaissementForm
    template_name = 'perfect/updat_encaissement.html'
    success_message = 'Entrée de caisse Modifiée avec succès✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('list_encaissement')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context
  
class UpdatDecaissementView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_decaisse'
    model = Decaissement
    form_class = UpdatDecaissementForm
    template_name = 'perfect/updat_decaissement.html'
    success_message = 'Sortir de caisse Modifiée avec succès✓✓'
    error_message = "Erreur de saisie ✘✘ "
    success_url = reverse_lazy ('list_decaissement')
    timeout_minutes = 120
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        reponse =  super().form_valid(form)
        messages.success(self.request, self.success_message)
        return reponse
    def form_invalid(self, form):
        reponse =  super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_group = self.request.user.groups.first()
        context['user_group'] = user_group.name if user_group else None
        context['catego_vehi'] = CategoVehi.objects.all()
        return context

class UpdateRecetView(LoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    login_url = 'login'
    permission_url = 'updat_recet'
    model = Recette
    form_class = UpdateRecetteForm
    template_name = "perfect/recet_update.html"
    success_message = 'Recette Modifiée avec succès✓✓'
    error_message = "Erreur de saisie✘✘ "
    success_url = reverse_lazy ('list_recet')
    timeout_minutes = 200
    def dispatch(self, request, *args, **kwargs):
        last_activity = request.session.get('last_activity')
        if last_activity:
            last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - last_activity > timedelta(minutes=self.timeout_minutes):
                logout(request)
                messages.warning(request, "Vous avez été déconnecté ")
                return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    def form_invalid(self, form):
        reponse = super().form_invalid(form)
        messages.success(self.request, self.error_message)
        return reponse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_form()
        list_recet = Recette.objects.filter(date_saisie=date.today())
        recets=self.get_object()
        context = {
            'list_recet':list_recet,
            'forms':forms,
            'recets':recets,
        }
        return context 
   