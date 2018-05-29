#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
from desk.models import RegistrationSite


# Check functions
def zero_member(ident):
    from repatriate.models import Person
    return Person.active_objects.filter(target__identifier=ident).count() == 0


def num_pm_existe(num_progres_menage):
    from repatriate.models import Target
    return Target.objects.filter(
        deleted=False,
        num_progres_menage=num_progres_menage).count() != 0


def site_not_existe(site_engistrement):
    return RegistrationSite.objects.filter(
        deactivate=False, confirmed=True, slug=site_engistrement
    ).count() != 0


def no_doc_with_num_pm(chef_doc, num_progres_menage):
    # print(chef_doc, ' iii ', num_progres_menage)
    if chef_doc == "sdoc" and num_progres_menage != "":
        return True
    return False


def requise_num_progres_menage(pays_asile, num_progres_menage, chef_doc):
    if pays_asile != "algerie" and num_progres_menage == "" and chef_doc == "formulaire_de_retour":
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
    print(tel)
    if not tel or tel == '0':
        return False
    print(len("{}".format(tel)))
    if len("{}".format(tel)) < 9:
        return True
    return False


def not_empty_num_progres_menage_alg(pays_asile, num_progres_menage):
    print(pays_asile, ' :: ', num_progres_menage)
    if pays_asile == "algerie" and num_progres_menage != "":
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
    # print(instance)
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