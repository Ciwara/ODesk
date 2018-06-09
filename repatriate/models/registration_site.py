#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging

from django.db import models

from mptt.models import TreeForeignKey
from desk.models import Provider, Entity

logger = logging.getLogger(__name__)


class RegistrationSManager(models.Manager):
    def get_queryset(self):
        return super(RegistrationSManager, self).get_queryset(
        ).filter(confirmed=False, deactivate=False)


class RegistrationSite(models.Model):

    slug = models.SlugField("Slug", max_length=15, primary_key=True)
    name = models.CharField(null=True, blank=True, max_length=200)
    active = models.BooleanField(default=True)
    locality = TreeForeignKey(Entity, null=True, related_name="site_localities")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)
    deactivate = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)

    objects = models.Manager()
    confirme_objects = RegistrationSManager()

    def __str__(self):
        return "{slug} ({name}) / {locality}".format(
            name=self.name, locality=self.locality, slug=self.slug)

    def active(self):
        return self.filter(active=True)


class RegistrationSiteProvider(models.Model):

    class Meta:
        app_label = 'repatriate'
        unique_together = (('provider', 'site'),)

    provider = models.ForeignKey(Provider, related_name="registration_providers")
    site = models.ForeignKey(RegistrationSite, related_name="registration_sites")
    role = models.CharField("Role", max_length=15, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.site, self.provider)
