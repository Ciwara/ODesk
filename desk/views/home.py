#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from rolepermissions.checkers import has_role

from desk.models import Entity, Provider
from repatriate.models import Target, Person
from django.core.mail import send_mail
from django.conf import settings
from desk.forms import ContactForm
from OIMDesk.roles import (
    DeskAssistantAdmin, DNDSTech, Admin, DeskControle)


def success_view(request):
    return HttpResponse('Success! Thank you for your message.')


def index(request):
    context = {'page_slug': 'index'}

    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, [settings.EMAIL_HOST_USER, 'ibfadiga@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
    context.update({"form": form})
    return render(request, 'index.html', context)


@login_required
def home(request, *args, **kwargs):
    context = {}
    prov = Provider.objects.get(username=request.user.username)
    if has_role(prov, [Admin, DNDSTech]):
        return render(request, 'home.html', context)
    if has_role(prov, [DeskAssistantAdmin]):
        return redirect("controle")
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
