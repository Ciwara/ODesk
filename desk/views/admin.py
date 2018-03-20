#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from desk.models.Entities import Entity
from desk.models.Providers import Provider
from desk.models.Numbers import PhoneNumber
from desk_tools.numbers import normalized_phonenumber
from desk.decorators import user_role_within, user_permission
from desk_tools.auth import (
    create_provider, send_new_account_email,
    random_password, get_new_roles_for)

logger = logging.getLogger(__name__)


class ProviderRoleLocationForm(forms.ModelForm):

    class Meta:
        model = Provider
        fields = ['role', 'location']

    def __init__(self, *args, **kwargs):
        requester = kwargs.pop('requester') or None
        super(ProviderRoleLocationForm, self).__init__(*args, **kwargs)

        # limit available roles
        self.fields['role'].choices = [
            (r.slug, r.name) for r in get_new_roles_for(requester)
        ]

        self.fields['location'] = forms.CharField(
            required=True,
            label=_("Entity"),
            initial=self.fields['location'].initial,
        )
        self.fields['location_name'] = forms.CharField(
            required=False,
            label=_("Entity Name"),
            widget=forms.TextInput(attrs={'readonly': True}),
        )

    def clean_location(self):
        return Entity.get_or_none(
            self.cleaned_data.get('location').strip())


class AddProviderForm(forms.ModelForm):

    class Meta:
        model = Provider
        fields = ['gender', 'title', 'maiden_name', 'first_name',
                  'middle_name', 'last_name', 'email', 'position',
                  'role', 'location']

    def __init__(self, *args, **kwargs):
        self.requester = kwargs.pop('requester') or None
        super(AddProviderForm, self).__init__(*args, **kwargs)

        # limit available roles
        self.fields['role'].choices = [
            (r.slug, r.name) for r in get_new_roles_for(self.requester)
        ]
        self.fields['role'].help_text = _(
            "Make sur to match role with proper location")

        # set default to most common
        self.fields['role'].initial = 'dtc'

        # make sure first and last name are filed
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['title'].required = True

        self.fields['location'] = forms.CharField(
            required=True,
            label=_("Entity"),
            initial="mali",
            help_text=_("SNISI Code for that entity"),
        )
        self.fields['location_name'] = forms.CharField(
            required=False,
            label=_("Entity Name"),
            help_text=_("Verify your Entity Code"),
            widget=forms.TextInput(attrs={'readonly': True}),
        )
        self.fields['phonenumber_flotte'] = forms.CharField(
            max_length=8,
            required=False,
            label=_("Flotte Number"),
            help_text=_("Only for Flotte Santé numbers"),
            widget=forms.NumberInput(attrs={})
        )
        self.fields['phonenumber_orange'] = forms.CharField(
            max_length=8,
            required=False,
            label=_("Orange Number"),
            help_text=_("Personnal Orange phone number"),
            widget=forms.NumberInput()
        )
        self.fields['phonenumber_malitel'] = forms.CharField(
            max_length=8,
            required=False,
            label=_("Malitel Number"),
            help_text=_("Personnal Malitel phone number"),
            widget=forms.NumberInput()
        )

    def clean(self):
        cleaned_data = super(AddProviderForm, self).clean()
        flotte = cleaned_data.get("phonenumber_flotte")
        orange = cleaned_data.get("phonenumber_orange")
        malitel = cleaned_data.get("phonenumber_malitel")

        if flotte is None and orange is None and malitel is None \
                and not self.requester.is_admin:
            raise forms.ValidationError(
                _("At least one phone number is required."))

    @classmethod
    def get_clean_number(cls, numbersent):
        if numbersent is None:
            return None
        normalized = normalized_phonenumber(numbersent)
        if normalized is None:
            raise forms.ValidationError(_("Invalid Phone Number: %(value)s"),
                                        code='invalid',
                                        params={'value': numbersent})
        if PhoneNumber.objects.filter(identity=normalized).count():
            pn = PhoneNumber.objects.get(identity=normalized)
            raise forms.ValidationError(
                _("Phone Number already in use by %(value)s"),
                code='invalid',
                params={'value': pn.provider})
        return normalized

    def clean_location(self):
        return Entity.get_or_none(
            self.cleaned_data.get('location').strip())

    def clean_phonenumber_flotte(self):
        return AddProviderForm.get_clean_number(
            self.cleaned_data.get('phonenumber_flotte') or None)

    def clean_phonenumber_orange(self):
        return AddProviderForm.get_clean_number(
            self.cleaned_data.get('phonenumber_orange') or None)

    def clean_phonenumber_malitel(self):
        return AddProviderForm.get_clean_number(
            self.cleaned_data.get('phonenumber_malitel') or None)


@login_required
@user_role_within(['desk_admin', 'desk_tech'])
def add_provider(request, **kwargs):
    context = {}
    # main infos form being sent
    if request.method == 'POST':
        form = AddProviderForm(request.POST, requester=request.user)
        if form.is_valid():
            numbers = []
            if form.cleaned_data.get('phonenumber_flotte'):
                numbers.append(
                    (form.cleaned_data.get('phonenumber_flotte'), True))
            if form.cleaned_data.get('phonenumber_orange'):
                numbers.append(
                    (form.cleaned_data.get('phonenumber_orange'), False))
            if form.cleaned_data.get('phonenumber_malitel'):
                numbers.append(
                    (form.cleaned_data.get('phonenumber_malitel'), False))
            try:
                provider, passwd = create_provider(
                    first_name=form.cleaned_data.get('first_name'),
                    last_name=form.cleaned_data.get('last_name'),
                    role=form.cleaned_data.get('role').slug,
                    location=form.cleaned_data.get('location').slug,
                    email=form.cleaned_data.get('email'),
                    middle_name=form.cleaned_data.get('middle_name'),
                    maiden_name=form.cleaned_data.get('maiden_name'),
                    gender=form.cleaned_data.get('gender'),
                    title=form.cleaned_data.get('title'),
                    position=form.cleaned_data.get('position'),
                    phone_numbers=numbers)
            except Exception as e:
                provider = None
                passwd = None
                logger.error("Unable to create provider")
                logger.exception(e)
                messages.error(request,
                               _("Unable to create this account. "
                                 "See error details bellow"))
            else:
                email_suffix = ""
                if provider and provider.email:
                    email_sent, x = send_new_account_email(
                        provider=provider, password=passwd,
                        creator=request.user)
                    if email_sent:
                        email_suffix = " Un email a été envoyé."

                messages.success(
                    request,
                    _("User account {provider} has been created with "
                      "username “{username}” "
                      "and password “{passwd}”.{email_suffix}")
                    .format(provider=provider,
                            username=provider.username,
                            passwd=passwd,
                            email_suffix=email_suffix))
                return redirect('admin_add_provider')
        else:
            messages.error(
                request,
                _("Unable to create this account. See error details bellow"))
    else:
        form = AddProviderForm(requester=request.user)

    context.update({'form': form})

    return render(request,
                  kwargs.get('template_name', "admin/add_provider.html"),
                  context)


@login_required
@user_role_within(['desk_admin', 'desk_tech'])
def reset_password(request, username):
    provider = Provider.get_or_none(username, with_inactive=True)
    if provider is None:
        messages.error(request, _("Unable to find this user account: `{}`")
                       .format(username))
        return redirect('home')
    if provider.role.slug in ('desk_admin', 'validation_bot'):
        messages.error(request, _("You can't reset password for {}")
                       .format(provider))
    else:
        passwd = random_password(dumb=True)
        provider.set_password(passwd)
        provider.save()
        messages.success(request,
                         _("Password for {provider} "
                           "has been changed to “{passwd}”.")
                         .format(provider=provider, passwd=passwd))
    return redirect('public_profile', username=username)


@login_required
@user_role_within(['desk_admin', 'desk_tech'])
def disable_provider(request, username):
    provider = Provider.get_or_none(username, with_inactive=True)
    if provider is None:
        messages.error(request, _("Unable to find this user account: `{}`")
                       .format(username))
        return redirect('home')
    if provider.role.slug in ('desk_admin', 'validation_bot'):
        messages.error(request, _("You can't disable “{}”")
                       .format(provider))
    else:
        provider.disable()
        messages.success(request,
                         _("{provider} has been disabled.")
                         .format(provider=provider))
    return redirect('public_profile', username=username)


@login_required
@user_role_within(['desk_admin'])
def enable_provider(request, username):
    provider = Provider.get_or_none(username, with_inactive=True)
    if provider is None:
        messages.error(request, _("Unable to find this user account: `{}`")
                       .format(username))
        return redirect('home')
    provider.enable()
    messages.success(request,
                     _("{provider} has been enabled.")
                     .format(provider=provider))
    return redirect('public_profile', username=username)


class FindPhoneNumberForm(forms.Form):

    number = forms.IntegerField(_("Phone Number"))


@login_required
@user_permission('monitor')
def find_phonenumber(request, **kwargs):
    context = {}
    numbers = None

    # main infos form being sent
    if request.method == 'POST':
        form = FindPhoneNumberForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('number')
            numbers = PhoneNumber.objects.filter(identity__icontains=query)
    else:
        form = FindPhoneNumberForm()

    context.update({'form': form,
                    'numbers': numbers})

    return render(request,
                  kwargs.get('template_name', "admin/find_phonenumber.html"),
                  context)


@login_required
@user_role_within(['desk_admin', 'desk_tech'])
def delete_phonenumber(request, identity):
    number = PhoneNumber.get_or_none(identity)
    if number is None:
        messages.error(request, _("Unable to find this phone number: “{}”")
                       .format(identity))
        return redirect('admin_find_phonenumber')
    number.delete()
    messages.success(request,
                     _("Phone number “{identity}” "
                       "has been removed and can be reused by someone else.")
                     .format(identity=identity))
    return redirect('admin_find_phonenumber')
