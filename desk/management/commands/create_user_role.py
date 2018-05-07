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
from desk.models import RegistrationSite, Project, Provider

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

        headers = ['identifiant', 'nom', 'prenom', 'email', 'tel',
                   'role', 'site', 'localite']
        input_file = open(options.get('input_file'), 'r', encoding='utf-8')
        csv_reader = csv.DictReader(input_file, fieldnames=headers)

        # cls = Entity
        for user in csv_reader:
            print(user)
            if csv_reader.line_num == 1:
                continue
            data = {
                "first_name": user.get('prenom'),
                "last_name": user.get('nom'),
                "project": Project.objects.get(slug="hcr"),
                "site": RegistrationSite.get(slug=user.get("site")),
                "email": user.get('email'),
                "tel": user.get('tel'),
            }
            prov = Provider.objects.get_or_create(
                username=user.get('identifiant'), **data)

            assign_role(prov, user.get("role"))
