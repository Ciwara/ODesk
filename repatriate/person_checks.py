#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

# Check functions


def num_pi_existe(num_progres_individuel):
    from repatriate.models import Person
    return Person.objects.filter(
        deleted=False,
        num_progres_individuel=num_progres_individuel).count() != 0


def no_doc_with_num_pi(chef_doc, num_progres_individuel):
    if chef_doc == "sdoc" and num_progres_individuel != "":
        return True
    return False


def requise_num_progres_individuel(pays_asile, num_progres_menage, chef_doc):
    if pays_asile == "algerie":
        return False
    if not num_progres_menage and chef_doc == "formulaire_de_retour":
        return True
    return False


def invalide_num_progres_individuel(num_pm):
    if num_pm:
        try:
            num_camp, incr = num_pm.split("-")
        except Exception:
            return True
        if len(incr) != 8:
            return True
    return False

