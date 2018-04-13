#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from desk.models import Entity, Provider
from repatriate.models import Target


def index(request):
    context = {'page_slug': 'index'}

    return render(request, 'index.html', context)


@login_required
def dashboard(request, *args, **kwargs):

    prov = None
    if request.user.is_authenticated():
        prov = Provider.objects.get(username=request.user.username)

    not_valid_soumissions_rep = Target.objects.filter(
        site_engistrement=prov.site, validation_status=Target.NOT_APPLICABLE)
    for v_soumissions in not_valid_soumissions_rep:
        v_soumissions.validated_url = reverse(
            "tvalidated", args=[v_soumissions.identifier])
    context = {'page_slug': 'dashboard',
               'not_valid_soumissions_rep': not_valid_soumissions_rep}

    return render(request, 'home.html', context)


@login_required
def desk_controle(request):

    context = {}
    return render(request, 'desk_controle.html', context)
