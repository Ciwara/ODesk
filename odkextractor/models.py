#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

# import json
# import re
# import logging

from django.utils import timezone
from django.db import models

from django.utils.translation import ugettext_lazy as _


class FormSettings(models.Model):
    form_id = models.SlugField(max_length=75, primary_key=True)
    app = models.CharField(max_length=100, default="ODK_B_v1.4.10.jar")
    odk_username = models.CharField(max_length=100)
    odk_password = models.CharField(max_length=100)
    export_directory = models.CharField(max_length=100, default="data")
    exclude_media_export = models.BooleanField(default=False)
    storage_directory = models.CharField(max_length=100, default="data")
    export_filename = models.CharField(max_length=100, default="data.csv")
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
        return self.form_id
