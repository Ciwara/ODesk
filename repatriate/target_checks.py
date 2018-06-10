#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from repatriate.models import RegistrationSite


# Check functions
def zero_member(ident):
    from repatriate.models import Person
    return Person.active_objects.filter(target__identifier=ident).count() == 0


def num_pm_existe(instance):
    if not instance.num_progres_menage:
        return False
    from repatriate.models import Target, DuplicateProgresMenage
    target = Target.active_objects.exclude(
        instance_id=instance.instance_id).filter(
        num_progres_menage=instance.num_progres_menage)
    if target.count() > 0:
        data = {
            "old_target": instance,
            "new_target": target[0]
        }
        DuplicateProgresMenage.objects.get_or_create(**data)


def site_not_existe(site_engistrement):
    if site_engistrement.deactivate or not site_engistrement.confirmed:
        return True
    return False


def no_doc_with_num_pm(chef_doc, num_progres_menage):
    # Un sans document ne peut pas avoir un numéro progres menage.
    if chef_doc == "sdoc" and num_progres_menage != "":
        return True
    return False


def requise_num_progres_menage(pays_asile, num_progres_menage):
    if pays_asile == "algerie":
        return False
    if not num_progres_menage:
        return True
    return False


def invalide_num_progres_menage(num_pm):
    if num_pm:
        try:
            num_camp, incr = num_pm.split("-")
        except Exception:
            return True
        if len(incr) != 8:
            return True
    return False


def invalide_num_tel(tel):
    if not tel or tel == '0':
        return False
    if len("{}".format(tel)) < 8:
        return True
    return False


def not_empty_num_progres_menage_alg(pays_asile, num_progres_menage):
    if pays_asile == "algerie" and num_progres_menage:
        return True
    return False


def many_chef_menage(instance):
    from repatriate.models import Person
    if Person.active_objects.filter(target=instance, membre_lien="chef_de_famille").count() > 1:
        return True
    return False


def no_chef_manage(instance):
    from repatriate.models import Person
    if Person.objects.filter(target=instance, membre_lien="chef_de_famille").count() == 0:
        return True
    return False
