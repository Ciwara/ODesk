#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.db import models


class Email(models.Model):
    """ Motification
    """
    P_OIM = "p_oim"
    P_HCR = "p_hcr"
    MDE = "mde"
    DNDS = "dmds"
    DNPSES = "dnpses"
    DFM = "dfm"

    TYPE = {
        P_OIM: ("Partenaire OIM"),
        P_HCR: ("Partenaire HCR"),
        MDE: ("Malien de l'exterieure"),
        DNDS: ("DNDS"),
        DNPSES: ("DNPSES"),
        DFM: ("DFM")
    }

    class Meta:
        app_label = 'desk'
        unique_together = (('name',),)
        # ordering = ['create_date', ]

    mail = models.EmailField(max_length=100, primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    group = models.CharField(max_length=10, choices=TYPE.items())

    def __str__(self):
        return "{name} {mail} {group}".format(
            name=self.name, mail=self.mail, group=self.group)
