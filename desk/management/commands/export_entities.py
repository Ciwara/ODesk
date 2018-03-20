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

from desk.models import Entity
from collections import OrderedDict


TODAY = datetime.date.today()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            help='CSV file to import from',
            action='store',
            dest='input_file'
        )
    en_types = OrderedDict([
        ("continent", "Continent"),
        ("country", "Pays"),
        ("region", "Région"),
        ("cercle", "Cercle"),
        ("commune", "Commune"),
        ("vfq", "Village")
    ])
    entity_name = {
        "continent": "continents",
        "country": "pays",
        "region": "regions",
        "cercle": "cercles",
        "commune": "communes",
        "vfq": "villages"
    }

    def handle(self, *args, **options):

        self.write_csv()

    def write_csv(self):
        headers = ["list_name", "name", "label", "continent",
                   "country", "region", "cercle", "commune"]
        print("Exportting countries...")

        fileoutname = "entity-{}.csv".format(TODAY.strftime("%d-%b-%Y"))
        with open(fileoutname, "w", newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for en_type in self.en_types.keys():
                for entity in Entity.objects.filter(type=en_type):
                    print("Slug : {} - Name : {} ".format(
                        entity.slug, entity.name))
                    writer.writerow(self.get_dic_entity(entity))

    def get_dic_entity(self, entity):
        data = {'list_name': self.entity_name.get(entity.type.slug),
                'name': entity.slug,
                'label': u"{}".format(entity.name),
                }
        if entity.parent:
            data[entity.parent.type.slug] = entity.parent.slug
        return data
