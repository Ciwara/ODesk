#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

# from optparse import make_option
# import glob
# import json
from django.core.management.base import BaseCommand
from odkextractor.models import (FormSettings)
from odkextractor.commons import get_odk_data

# from desk.models import Entity
OTHER = "other"


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-pk',
            help='json file to import from',
            action='store',
            dest='input_file'
        )

    def handle(self, *args, **options):
        print("handle")
        for form in FormSettings.objects.filter(active=True):
            get_odk_data(form)
