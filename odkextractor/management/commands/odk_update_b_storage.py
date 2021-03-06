#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.core.management.base import BaseCommand
from odkextractor.models import (FormID)
from odkextractor.commons import get_odk_data, read_csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        forms = FormID.objects.filter(active=True)
        if FormID.IN_PROGRESS not in [f.status for f in forms]:
            for form in forms:
                try:
                    form.in_progress()
                    get_odk_data(form)
                except Exception as e:
                    pass
                form.clean_media()
                form.not_in_progress()
                read_csv(form.get_migrant_csv_file, form.data_json)
                read_csv(form.get_ig_manage_csv_file, form.data_info_g_json)
