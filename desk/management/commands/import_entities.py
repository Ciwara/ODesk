#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

# from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.management import call_command

import csv

from desk.models import Entity, EntityType


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            help='CSV file to import from',
            action='store',
            dest='input_file'
        )

    def handle(self, *args, **options):

        headers = ['type', 'code', 'name', 'parent']
        input_file = open(options.get('input_file'), 'r', encoding='utf-8')
        csv_reader = csv.DictReader(input_file, fieldnames=headers)

        if options.get('clear'):
            print("Removing all countries...")
            EntityType.objects.all().delete()
            Entity.objects.all().delete()
            print("Importing fixtures")
            call_command("loaddata", "fixtures/EntityType.xml")
            call_command("loaddata", "fixtures/Entity-root.xml")

        print("Importing countries...")

        for entry in csv_reader:
            if csv_reader.line_num == 1:
                continue
            slug = entry.get('code')
            name = entry.get('name')
            # print("Name : {} Slug : {}".format(name, slug))
            entity_type = entry.get('type')
            parent_slug = entry.get('parent')
            try:
                entity_type = EntityType.objects.get(slug=entity_type)
            except:
                pass
            try:
                entity_parent = Entity.objects.get(slug=parent_slug)
            except:
                entity_parent = None

            latitude = entry.get('latitude')
            longitude = entry.get('longitude')

            try:
                entity = Entity.objects.create(
                    slug=slug,
                    name=name,
                    type=entity_type,
                    parent=entity_parent,
                    latitude=latitude or None,
                    longitude=longitude or None)
            except Exception as e:
                print("Entity :", e)
