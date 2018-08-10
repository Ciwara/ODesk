#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
from django.db import models
from django.utils import timezone
from desk.tools import share_by_mail


logger = logging.getLogger(__name__)


class Report(models.Model):

    SITREP = 'sitrep'
    CMP = 'cmp'
    DTM = 'dtm'
    TYPE_REPORT = {
        SITREP: ("SITREP"),
        CMP: ("CMP"),
        DTM: ("DTM")
    }

    class Meta:
        app_label = 'desk'
        unique_together = (('name',),)
        ordering = ['create_date', ]

    name = models.CharField(verbose_name="N°", max_length=50, primary_key=True)
    category = models.CharField(
        verbose_name="Catégorie", max_length=10, choices=TYPE_REPORT.items())
    description = models.TextField(
        verbose_name="Description", max_length=100, null=True, blank=True)
    publish_date = models.DateTimeField(
        verbose_name="Date de publication", default=timezone.now)
    create_date = models.DateField(verbose_name="Date du rapport")
    doc_file = models.FileField(upload_to='reports/')

    def __str__(self):
        return "{name} / {publish_date}".format(
            name=self.name, publish_date=self.publish_date)

    @property
    def subject(self):
        return "Nouveau rapport {} {}.".format(self.name, self.category)

    def with_media(self):
        return True

    @property
    def media_file(self):
        return self.doc_file.name

    @property
    def msg_body(self):
        return "<h3>Hi,</h3> Nouveau rapport {cat} {name} <br>{desc}.\
            <br> Du {date} est disponible sur <a href={link}>{link}</a>".format(
            cat=self.category,
            name=self.name,
            desc=self.description,
            date=self.create_date,
            link="http://msah.ml"
        )

models.signals.post_save.connect(share_by_mail, sender=Report)
