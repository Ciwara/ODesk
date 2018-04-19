#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

# import json
# import re
# import logging
import os
from django.utils import timezone
from collections import OrderedDict
from django.db import models

from django.utils.translation import ugettext_lazy as _


class ODKSetting(models.Model):

    app = models.CharField(max_length=100, default="ODK_B_v1.4.10.jar")
    odk_username = models.CharField(max_length=100)
    odk_password = models.CharField(max_length=100)
    export_directory = models.CharField(max_length=100, default="data")
    storage_directory = models.CharField(max_length=100, default="data")
    aggregate_url = models.CharField(max_length=250)
    active = models.BooleanField(default=True)
    last_update = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_or_create(cls, slug, name):
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return cls.objects.create(slug=slug, name=name)

    def __str__(self):
        return "{}/{}/{}".format(
            self.aggregate_url, self.active, self.last_update)


class FormID(models.Model):

    IN_PROGRESS = 'en cours'
    NOT_IN_PROGRESS = 'not in progress'
    STATUS = OrderedDict([
        (IN_PROGRESS, "En cours"),
        (NOT_IN_PROGRESS, "Pas en cours")
    ])

    form_id = models.SlugField(max_length=75, primary_key=True)
    export_filename = models.CharField(max_length=100, default="data.csv")
    exclude_media_export = models.BooleanField(default=False)
    last_update = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    odk_setting = models.ForeignKey(ODKSetting,
                                    related_name='odk_settings')

    status = models.CharField(max_length=20, choices=STATUS.items(),
                              default=NOT_IN_PROGRESS)

    def __str__(self):
        return self.form_id

    def get_path(self, path_):
        return os.path.join(
            os.path.join(
                os.getcwd(), "odkextractor"), *path_.split(','))

    def in_progress(self):
        self.status = self.IN_PROGRESS
        self.save()

    def not_in_progress(self):
        self.status = self.NOT_IN_PROGRESS
        self.save()

    @property
    def get_migrant_csv_file(self):
        return self.get_path("{},{}".format(self.odk_setting.export_directory,
                                            self.export_filename.replace('-', '_')))

    @property
    def get_ig_manage_csv_file(self):
        return os.path.splitext(
            self.get_migrant_csv_file)[0] + "_informations_generales_menage_membre_menage.csv"

    @property
    def data_json(self):
        return os.path.splitext(self.get_migrant_csv_file)[0] + ".json"

    @property
    def data_info_g_json(self):
        return os.path.splitext(self.get_ig_manage_csv_file)[0] + ".json"
