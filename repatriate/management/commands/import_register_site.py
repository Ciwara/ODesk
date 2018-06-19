#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

# from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.management import call_command

import csv

from desk.models import Entity

from repatriate.models import RegistrationSite


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            help='CSV file to import from',
            action='store',
            dest='input_file'
        )

    def handle(self, *args, **options):

        headers = ['code', 'name', 'locality', 'latitude', 'longitude', 'geometry']

        input_file = open(options.get('input_file'), 'r', encoding='utf-8')
        csv_reader = csv.DictReader(input_file, fieldnames=headers)

        # print("Importing countries...")
        for entry in csv_reader:
            if csv_reader.line_num == 1:
                continue
            slug = entry.get('code')
            name = entry.get('name')
            locality = entry.get('locality')
            latitude = entry.get('latitude')
            longitude = entry.get('longitude')
            geometry = entry.get('geometry')

            try:
                locality_ = Entity.objects.get(slug=str(locality))
            except Exception as e:
                print(e)
            try:
                r_site = RegistrationSite.objects.create(
                    slug=slug,
                    name=name,
                    locality=locality_,
                    # latitude=latitude,
                    # longitude=longitude,
                    # geometry=geometry,
                )
            except Exception as e:
                print(e)
            # print(r_site)
