#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import datetime
import csv
# from optparse import make_option
from django.core.management.base import BaseCommand

from migrants.models import Person


TODAY = datetime.date.today()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-r',
            help='CSV file to import from',
            action='store',
            dest='input_file'
        )

    def handle(self, *args, **options):

        self.write_csv()

    def write_csv(self):
        headers = ["Identifiant", "nom", "prenom", "sexe", "Âge", "Telephone",
                   "Région", "Cercle", "Commune"]

        fileoutname = "region-kayes-{}.csv".format(TODAY.strftime("%d-%b-%Y"))
        with open(fileoutname, "w", newline='',
                  encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for member in Person.objects.filter(survey__lieu_region="kayes"):
                print(member)
                writer.writerow(self.get_dic_entity(member))

    def get_sex(self, sex):
        print(sex)
        return "M" if sex.lower() == "male" else "F"

    def get_dic_entity(self, member):
        data = {'Identifiant': member.identifier,
                'Nom': member.nom,
                'Prénom': member.prenoms,
                'Sexe': self.get_sex(member.gender),
                "Âge": member.age,
                "Telephone": member.survey.tel,
                "Région": member.survey.lieu_region.upper(),
                "Cercle": member.survey.lieu_cercle.upper(),
                "Commune": member.survey.lieu_commune.upper()
                }
        return data
