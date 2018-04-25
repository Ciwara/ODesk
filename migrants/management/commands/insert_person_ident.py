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

from migrants.models import Person
from collections import OrderedDict


TODAY = datetime.date.today()


class Command(BaseCommand):

    en_types = OrderedDict([
        ("kayes-cercle", 11),
        ("diema", 13),
        ("nioro", 16),
        ("kita", 15),
        ("bafoulabe", 12),
        ("yelimane", 17),
        ("kenieba", 14)
    ])

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            help='CSV file to import from',
            action='store',
            dest='input_file'
        )

    def handle(self, *args, **options):

        for member in Person.objects.filter(
                survey__adresse_mali_lieu_region="kayes").order_by("survey__submission_date"):
            member.identifier = self.create_identifier(member)
            member.save()
            print(self.create_identifier(member))

    def create_identifier(self, m):
        try:
            p_lastest = Person.objects.filter(
                survey__adresse_mali_lieu_cercle=m.survey.adresse_mali_lieu_cercle).latest("identifier")
            identifier = p_lastest.identifier[6:]
        except Exception as e:
            print(e)
            identifier = "00000"
        if not identifier:
            identifier = "00000"

        return "R01{c}{id}".format(
            c=self.get_slug_cercle(m.survey.adresse_mali_lieu_cercle),
            id=self.add(identifier, "1"))

    def get_slug_cercle(self, cercle):
        c_id = self.en_types.get(cercle)
        return self.add("000", str(c_id))

    def add(self, x, y):
        # print(x, "R", y)
        return str(int(x) + int(y)).zfill(len(x))
