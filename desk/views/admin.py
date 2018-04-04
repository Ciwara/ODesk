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
from desk.decorators import user_role_within

logger = logging.getLogger(__name__)


class AddProviderForm(forms.ModelForm):

    class Meta:
        model = Provider
        fields = ['gender', 'title', 'maiden_name', 'first_name',
                  'middle_name', 'last_name', 'email', 'position',
                  'role', 'location']


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
