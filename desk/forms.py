#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
from datetime import date
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# from django.contrib.auth.models import Group

from desk.models import (Provider, Report)


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)


# class LoginForm(forms.Form):
#     username = forms.CharField(max_length=255, required=True)
#     password = forms.CharField(widget=forms.PasswordInput, required=True)

#     def clean(self):
#         username = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')
#         user = authenticate(username=username, password=password)
#         if not user or not user.is_active:
#             raise forms.ValidationError(
#                 "Sorry, that login was invalid. Please try again.")
#         return self.cleaned_data

#     def login(self, request):
#         username = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')
#         user = authenticate(username=username, password=password)
#         return user


class UserCreationForm(forms.ModelForm):
    """ A form for creating new users. Includes all the required fields, plus a
        repeated password.
    """

    class Meta:
        model = Provider
        fields = ('username', 'gender', 'title', 'first_name', 'last_name',
                  'phone', 'phone2', 'project', 'email', 'groups')
        # exclude = ['email']

        # widgets = {
        # }

    password1 = forms.CharField(
        label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Confirmation', widget=forms.PasswordInput)

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "Les mots de passe ne correspondent pas")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ReportForm(forms.ModelForm):

    create_date = forms.DateField(initial=date.today,
        input_formats=["%d %m %Y"], widget=forms.DateInput(
            attrs={'class': 'datepicker form-control'}))

    class Meta:
        model = Report
        fields = [
            'category', 'name', 'create_date', 'description', 'doc_file',
        ]
        # exclude = []

    def clean_create_date(self):
        print("EEE : ", self.cleaned_data['create_date'])
        # d, m, y = self.cleaned_data.get('create_date').split("-")
        # create_date = date(y, m, d)
        return self.cleaned_data['create_date']


class UserChangeForm(forms.ModelForm):

    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Provider

        fields = ('title', 'first_name', 'last_name', 'gender',
                  'email', 'phone', 'phone2', 'project', 'email', 'groups', 'is_active')
        exclude = ['is_admin', "password"]

    # def clean_password(self):
    #     return self.initial["password"]
