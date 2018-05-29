#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django import forms
# from django.contrib.admin import widgets

from django.core.exceptions import ValidationError

from repatriate.person_checks import (
    invalide_num_progres_individuel,
    requise_num_progres_individuel)
from repatriate.target_checks import (
    invalide_num_progres_menage, not_empty_num_progres_menage_alg,
    invalide_num_tel, no_doc_with_num_pm, requise_num_progres_menage)
from repatriate.models import Person, Target


class SearchFormPerPeriod(forms.Form):

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker form-control', 'size': '10'}))
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker form-control', 'size': '10'}))


class SearchForm(forms.Form):

    num_progres_individuel = forms.CharField(
        label="Numéro de progres individuel", required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de progres individuel'}),)

    def get_result(self, required):
        try:
            result = Person.objects.get(
                num_progres_individuel=self.cleaned_data.get('num_progres_individuel'))
        except Exception:
            result = "Aucun resultat"
        return result


class TargetForm(forms.ModelForm):

    class Meta:
        model = Target
        exclude = []
        fields = [
            'date_arrivee',
            'chef_doc',
            'site_engistrement',
            'nu_enregistrement',
            'pays_asile',
            'num_progres_menage',
            'point_de_entree',
            'num_doc',
            'tel',
            'tel2'
        ]

        date_arrivee = forms.DateField(
            widget=forms.DateInput(format='%m/%d/%Y'),
            input_formats=('%m/%d/%Y', )
        )

    def clean_num_progres_menage(self):

        num_progres_menage = self.cleaned_data.get('num_progres_menage')
        chef_doc = self.cleaned_data.get('chef_doc')
        pays_asile = self.cleaned_data.get('pays_asile')

        if not_empty_num_progres_menage_alg(pays_asile, num_progres_menage):
            raise ValidationError("Algerie n'a pas de numéro progres menage.")

        if no_doc_with_num_pm(chef_doc, num_progres_menage):
            raise ValidationError(
                "Un sans document ne peut pas avoir un numéro progress.")

        if requise_num_progres_menage(pays_asile, num_progres_menage, chef_doc):
            raise ValidationError(
                "Avec un VRF le numéro progres ménage est obligatoire")

        if invalide_num_progres_menage(num_progres_menage):
            raise ValidationError("Numéro progres invalide XXX-YYYYYYYY")

    def clean_tel(self):
        tel = self.cleaned_data.get('tel')
        if invalide_num_tel(tel):
            raise ValidationError("Numéro de tel incorrecte.")


class FixedPersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = [
            'membre_nom',
            'membre_prenom',
            'membre_sexe',
            'membre_ddn',
            'membre_age',
            'membre_age_mois',
            'membre_lien',
            'membre_scolaire',
            'num_progres_individuel',
            'membre_vulnerabilite',
            'dispo_doc_etat_civil',
            'num_acte_naissance',
            'num_acte_mariage',
            'num_carte_nina',
            'num_carte_identite_national',
            'num_passeport',
            'nom_pere',
            'prenom_pere',
            'profession_pere',
            'niveau_education_pere',
            'nom_mere',
            'prenom_mere',
            'profession_mere',
            'niveau_education_mere',
            'profession',
            'existe_centre_etat_civil',
            'centre_etat_civil',
            'au_moins_deux_temoins',
            'referer',
            'a_qui',
        ]
        exclude = []

    def clean_num_progres_individuel(self):
        num_progres_individuel = self.cleaned_data.get('num_progres_individuel')
        if invalide_num_progres_individuel(num_progres_individuel):
            raise ValidationError("Numéro progres invalide XXX-YYYYYYYY")
