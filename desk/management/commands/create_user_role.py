#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import datetime
import csv
# from optparse import make_option
from django.core.management.base import BaseCommand
# from django.core.management import call_command
from rolepermissions.roles import assign_role
from repatriate.models import RegistrationSite, RegistrationSiteProvider
from desk.models import Project, Provider, EntityProvider, Entity

TODAY = datetime.date.today()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            help='CSV file to import from',
            action='store',
            dest='input_file'
        )

    def handle(self, *args, **options):

        headers = [
            'identifiant', 'nom', 'prenom', 'sexe', 'email', 'tel',
            'remove_role', 'add_role', 'site', 'is_active', 'locality']
        input_file = open(options.get('input_file'), 'r', encoding='utf-8')
        csv_reader = csv.DictReader(input_file, fieldnames=headers)

        for row_user in csv_reader:
            if csv_reader.line_num == 1:
                continue
            data = {
                "first_name": row_user.get('prenom'),
                "last_name": row_user.get('nom'),
                "project": Project.objects.get(slug="hcr"),
                "email": row_user.get('email'),
                "phone": row_user.get('tel'),
                "is_active": True if row_user.get('is_active')=="oui" else False
            }
            # print(user)
            # Add or update provider
            prov, ok = Provider.objects.update_or_create(
                username=row_user.get('identifiant'), defaults=data)
            prov.set_password(row_user.get('identifiant'))
            prov.save()

            # Add RegistrationSiteProvider
            for site_name in row_user.get("site").split("_"):
                print(site_name)
                try:
                    rsite = RegistrationSite.objects.get(name=site_name)
                except Exception as e:
                    print("Site : {} error :{}".format(site_name, e))
                    continue
                try:
                    RegistrationSiteProvider.objects.get_or_create(
                        provider=prov, site=rsite)
                except Exception as e:
                    print(e)
            # Add role
            for role in row_user.get("add_role").split(" "):
                print(role)
                assign_role(prov, role)
                if role == "desk_analyse":
                    for locality in row_user.get("locality").split("_"):
                        try:
                            EntityProvider.objects.get_or_create(
                                provider=prov, locality=Entity.objects.get(slug=locality))
                        except Exception as e:
                            raise
