#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

# import json
# import re
# import logging

from django.utils import timezone
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
        return "{}-{}-{}".format(
            self.odk_username, self.active, self.last_update)


class FormID(models.Model):

    form_id = models.SlugField(max_length=75, primary_key=True)
    export_filename = models.CharField(max_length=100, default="data.csv")
    exclude_media_export = models.BooleanField(default=False)
    last_update = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    odk_setting = models.ForeignKey(ODKSetting,
                                    related_name='odk_settings')

    def __str__(self):
        return self.form_id
