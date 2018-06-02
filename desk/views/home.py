#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect

# from rolepermissions.decorators import has_role_decorator
# from rolepermissions.decorators import has_permission_decorator
# from rolepermissions.roles import get_user_roles
from rolepermissions.checkers import has_role

from desk.models import Entity, Provider
from repatriate.models import Target, Person
from django.core.mail import send_mail
from OIMDesk.roles import (
    DeskAssistantAdmin, DNDSTech, DeskAdmin, DeskControle)


def index(request):
    context = {'page_slug': 'index'}

    # if form.is_valid():
    #     subject = form.cleaned_data['subject']
    #     message = form.cleaned_data['message']
    #     sender = form.cleaned_data['sender']
    #     cc_myself = form.cleaned_data['cc_myself']
    #     recipients = ['faddev@gmail.com']

    #     if cc_myself:
    #         recipients.append(sender)

    #     send_mail(subject, message, sender, recipients)
    #     return HttpResponseRedirect('/')

    return render(request, 'index.html', context)


@login_required
def home(request, *args, **kwargs):
    context = {}
    prov = Provider.objects.get(username=request.user.username)
    if has_role(prov, [DeskAdmin, DeskAssistantAdmin, DNDSTech]):
        return render(request, 'home.html', context)
    if prov.project.slug == "hcr":
        return redirect("dashboard_rep")
    if prov.project.slug == "oim":
        return redirect("dashboard_mig")
    if prov.project.slug == "all":
        return render(request, 'home.html', context)
    else:
        return redirect("/")


@login_required
# @has_permission_decorator("controle_data")
def dashboard(request, *args, **kwargs):

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
