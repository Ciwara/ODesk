#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django import forms
# from django.contrib.admin import widgets

# from migrants.models import Person, Survey


class SearchFormPerPeriod(forms.Form):

    start_date = forms.DateField(
        label="Date de debut",
        widget=forms.DateInput(
            attrs={'class': 'datepicker form-control', 'size': '5'}))
    end_date = forms.DateField(
        label="Date de fin",
        widget=forms.DateInput(
            attrs={'class': 'datepicker form-control', 'size': '5'}))


class SearchMigrantForm(forms.Form):

    migrant = forms.CharField(
        label="Recherche", max_length=200, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'rechercher par numéro'}))
