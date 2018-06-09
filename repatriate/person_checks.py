#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

# Check functions


def no_doc_with_num_pi(pn, num_progres_individuel):
    if pn.target.chef_doc == "sdoc" and num_progres_individuel:
        return True
    return False


def requise_num_progres_individuel(pn, num_progres_individuel):
    if pn.target.pays_asile == "algerie":
        return False
    if not num_progres_individuel and pn.target.chef_doc == "formulaire_de_retour":
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
