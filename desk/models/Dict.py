#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
from django.db import models

logger = logging.getLogger(__name__)


class DictLabel(models.Model):

    class Meta:
        app_label = 'desk'
        unique_together = (('name_md', 'code'),)

    name_md = models.CharField("Nom du models", max_length=50)
    code = models.SlugField(max_length=50, primary_key=True)
    label = models.CharField(max_length=100)

    def __str__(self):
        return "{name_md} / {label}".format(
            name_md=self.name_md, label=self.label)
