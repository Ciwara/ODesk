#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django import forms
# from django.contrib.admin import widgets

from repatriate.models import Person, Target


class SearchFormPerPeriod(forms.Form):
    star_date = forms.DateField()
    end_date = forms.DateField()
    # widgets = forms.DateInput(attrs={'class': 'datepicker'}),


class SearchForm(forms.Form):

    num_progres_individuel = forms.CharField(
        label="Numéro de progres individuel", max_length=200, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'recherche par numéro'}),)

    def get_result(self, required):
        try:
            result = Person.objects.get(
                num_progres_individuel=self.cleaned_data.get('num_progres_individuel'))
        except Exception:
            result = None
        return result
