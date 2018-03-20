#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
# import os
# import qrcode

from django.db import models


class Vulnerability(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return "{slug} - {name}".format(slug=self.slug, name=self.name)


class Camp(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return "{slug} - {name}".format(slug=self.slug, name=self.name)


class Organization(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return "{slug} - {name}".format(slug=self.slug, name=self.name)


class Lien(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return "{slug} - {name}".format(slug=self.slug, name=self.name)


class TypeAssistance(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return "{slug} - {name}".format(slug=self.slug, name=self.name)


class NiveauxScolaire(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return "{slug} - {name}".format(slug=self.slug, name=self.name)


class Activite(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return "{slug} - {name}".format(slug=self.slug, name=self.name)
