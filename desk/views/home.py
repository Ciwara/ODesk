#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from desk.models import Entity, Provider
from repatriate.models import Target, Person


def index(request):
    context = {'page_slug': 'index'}

    return render(request, 'index.html', context)


@login_required
def dashboard(request, *args, **kwargs):

    prov = None
    if request.user.is_authenticated():
        prov = Provider.objects.get(username=request.user.username)
    target_per_site = Target.objects.filter(
        site_engistrement=prov.site)
    person_per_site = Person.objects.filter(
        target__site_engistrement=prov.site)
    not_valid_soumissions_rep = target_per_site.filter(
        validation_status=Target.NOT_APPLICABLE)

    total_person = target_per_site.count()
    total_male = person_per_site.filter(membre_sexe=Person.MALE).count()
    total_female = person_per_site.filter(membre_sexe=Person.FEMALE).count()
    nb_soumission = target_per_site.count()
    for v_soumissions in not_valid_soumissions_rep:
        v_soumissions.validated_url = reverse(
            "tvalidated", args=[v_soumissions.identifier])

    context = {'page_slug': 'dashboard',
               'nb_soumission': nb_soumission,
               'total_person': total_person,
               'total_male': total_male,
               'total_female': total_female,
               'not_valid_soumissions_rep': not_valid_soumissions_rep}

    return render(request, 'home.html', context)


@login_required
def desk_controle(request):

    context = {}
    return render(request, 'desk_controle.html', context)
