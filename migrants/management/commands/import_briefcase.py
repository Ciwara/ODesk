#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import PY2
from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.management import call_command

if PY2:
    import unicodecsv as csv
else:
    import csv


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            help='cs file to import from',
            action='store',
            dest='add_survey',
        )

        parser.add_argument(
            '-m',
            help='cs file to import from',
            action='store',
            dest='add_person',
        )

    def handle(self, *args, **options):

        survey_headers = [
            "SubmissionDate",
            "formhub-uuid",
            "date",
            "debut",
            "fin max_year",
            "operation-repatriement-type-operation",
            "operation-repatriement-cause",
            "operation-repatriement-cause_other",
            "operation-repatriement-nom-agent",
            "operation-repatriement-date-arrivee operation-repatriement-date-ebtretien",
            "informations-generales-menage-menage-pays-provenance",
            "informations-generales-menage-menage-ville",
            "informations-generales-menage-menage-point-entrer",
            "informations-generales-menage-menage-doc-voyage",
            "informations-generales-menage-menage-numero-doc-voyage",
            "informations-generales-menage-menage-photo-doc-voyage",
            "informations-generales-menage-menage-bien-pays-provenance",
            "informations-generales-menage-n1",
            "SET-OF-informations-generales-menage-membre-menage",
            "informations-generales-menage-membre-pays-provenance",
            "informations-generales-menage-nb-membre",
            "informations-generales-menage-reour-rejoidre-famille",
            "informations-generales-menage-faire-venir-famille",
            "adresse-mali-lieu_region",
            "adresse-mali-lieu_cercle",
            "adresse-mali-lieu_commune",
            "adresse-mali-lieu_village_autre adresse-mali-rue",
            "adresse-mali-porte  adresse-mali-tel",
            "type-hebergement-hebergement",
            "type-hebergement-hebergement_other",
            "sante-appui-bonne-sante sante-appui-maladie-chronique",
            "sante-appui-maladie-chronique_other",
            "sante-appui-prise-medicaments",
            "sante-appui-medicaments formation-experience-fromation-pro",
            "formation-experience-domaine",
            "formation-experience-metier",
            "formation-experience-secteur",
            "reinsertion-professionnelle-F1",
            "reinsertion-professionnelle-F2",
            "reinsertion-professionnelle-F3",
            "reinsertion-professionnelle-F4",
            "reinsertion-professionnelle-F5",
            "reinsertion-professionnelle-F6-activite_region",
            "reinsertion-professionnelle-F6-activite_cercle",
            "reinsertion-professionnelle-F6-activite_commune",
            "reinsertion-professionnelle-F6-activite_village_autre",
            "observations",
            "n2",
            "meta-instanceID",
            "KEY",
        ]

        menage_headers = [
            "membre-nationalite",
            "membre-prenoms",
            "membre-nom",
            "membre-sexe membre-type-naissance",
            "membre-annee-naissance",
            "membre-ddn",
            "membre-age",
            "membre-age1",
            "membre-profession",
            "membre-profession_other",
            "membre-etat-civil",
            "membre-lien",
            "membre-niveau-scolaire",
            "membre-document",
            "membre-num-doc",
            "membre-nina membre-biometric",
            "saisie-nina saisie-biometric",
            "membre-vulnerabilite",
            "membre-vul1",
            "membre-vul2",
            "membre-vul3",
            "photo-membre",
            "PARENT_KEY",
            "KEY SET-OF-membre-menage"]

        # if options.get('add_person'):
        input_file_ = open(options.get('add_person'), 'r')
        csv_reader = csv.DictReader(input_file_,
                                    fieldnames=menage_headers)
        self.add_person(csv_reader)
        # if options.get('add_survey'):
        input_file_ = open(options.get('add_survey'), 'r')
        csv_reader = csv.DictReader(
            input_file_, fieldnames=survey_headers)
        self.add_survey(csv_reader)

    def add_survey(self, csv_reader):
        print("Importing add_survey...")
        for entry in csv_reader:
            print(entry)
            if csv_reader.line_num == 1:
                continue
            print(entry.get("operation-repatriement-cause"))

    def add_person(self, csv_reader):
        print("Importing add_person...")
        for entry in csv_reader:
            print(entry)
            if csv_reader.line_num == 1:
                continue
            print("{} {}".format(
                entry.get("membre-nom"), entry.get("PARENT_KEY  ")))
