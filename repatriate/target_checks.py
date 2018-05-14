#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
from desk.models import RegistrationSite


# Check functions
def zero_member(instance):
    return instance.get_membres().count() == 0


def num_pm_existe(instance):
    from repatriate.models import Target
    return Target.objects.filter(
        deleted=False,
        num_progres_menage=instance.num_progres_menage).count() != 0


def site_not_existe(instance):
    return RegistrationSite.objects.filter(
        deactivate=False, confirmed=True, slug=instance.site_engistrement
    ).count() != 0


def no_doc_with_num_pm(instance):
    if instance.chef_doc == "sans_doc" and instance.num_progres_menage != "":
        return True
    return False


def requise_num_progres_menage(instance):
    if instance.pays_asile != "aligerie" and instance.num_progres_menage == "":
        return True
    return False


def invalide_num_progres_menage(instance):
    if instance.num_progres_menage:
        try:
            num_camp, incr = instance.num_progres_menage.split("-")
        except Exception:
            return True
        if len(incr) != 8:
            return True
    return False


def invalide_num_tel(instance):
    if len("{}".format(instance.tel)) < 8 and instance.tel == 0:
        return True
    return False


def not_empty_num_progres_menage_alg(instance):
    if instance.pays_asile == "algerie" and instance.num_progres_menage != "":
        return True
    return False


def many_chef_menage(instance):
    from repatriate.models import Person
    if Person.objects.filter(target=instance, membre_lien="chef_de_famille").count() > 1:
        return True
    return False


def no_chef_manage(instance):
    from repatriate.models import Person
    if Person.objects.filter(target=instance, membre_lien="chef_de_famille").count() < 1:
        return True
    return False


def checker(sender, instance, *args, **kwargs):

    targ = instance
    targ.is_zero_member = zero_member(instance)
    targ.is_requise_num_progres_menage = requise_num_progres_menage(instance)
    targ.is_invalide_num_progres_menage = invalide_num_progres_menage(instance)
    targ.is_invalide_num_tel = invalide_num_tel(instance)
    targ.is_not_empty_num_progres_menage_alg = not_empty_num_progres_menage_alg(instance)
    targ.is_many_chef_menage = many_chef_menage(instance)
    targ.is_no_chef_manage = no_chef_manage(instance)
    targ.is_no_doc_with_num_pm = no_doc_with_num_pm(instance)
    targ.is_site_not_existe = site_not_existe(instance)
    targ.save()
