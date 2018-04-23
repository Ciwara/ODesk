#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

# from optparse import make_option
from django.core.management.base import BaseCommand

# from migrants.models import Survey
from odkextractor.models import FormID


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            help='CSV file to import from',
            action='store',
            dest='input_file'
        )
        parser.add_argument(
            '-aa',
            help='CSV file to import from',
            action='store',
            dest='active_all'
        )
        parser.add_argument(
            '-ad',
            help='CSV file to import from',
            action='store',
            dest='deactive_all'
        )

    def handle(self, *args, **options):
        if options.get("active_all"):
            print("active all FormID...")
            for f in FormID.objects.all():
                f.active = True
                f.save()

        if options.get("deactive_all"):
            print("deactive all FormID...")
            for f in FormID.objects.all():
                f.active = False
                f.save()
