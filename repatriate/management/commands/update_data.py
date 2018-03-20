#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

# from optparse import make_option
# import glob
# import json
from django.core.management.base import BaseCommand

from desk.ona import get_form_data
from repatriate.models import (
    TargetTypeAssistance, TypeAssistance, Lien,
    OrganizationTarget, Activite, NiveauxScolaire, Collect, Target,
    Settings, Person, Organization, ContactTemoin, Camp,
    Vulnerability, VulnerabilityPerson)

# from desk.models import Entity
OTHER = "other"


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-pk',
            help='json file to import from',
            action='store',
            dest='input_file'
        )

    def get_bol(self, value):
        # print("", value)
        if value:
            value = value.strip()
        if value in ["OUI", "oui", "yes"]:
            return True
        else:
            return False

    def get_sex(self, sex):
        return "male" if sex.lower() == "masculin" else "female"

    def get_etat_civil(self, value):
        return "celibataire" if value.lower() == "celibataire" else "marie"

    def handle(self, *args, **options):
        self.setup()

    def get_or_other(self, value):
        print(value)
        if not value:
            "{}_other".format(value)
        return value

    def get_with_other(self, value):
        print(value)
        if not value:
            "{}_other".format(value)
        return value

    def setup(self):
        collect = Collect.objects.get(name="Formulaire rapatiment")
        rdata = get_form_data(collect.ona_form_pk)
        for targ in rdata:
            print("Nom {} : prénom {} Activite {}".format(
                targ.get("generales-chef-manage/chef_nom"),
                targ.get("generales-chef-manage/chef_prenom"),
                targ.get('generales-chef-manage/chef_profession')))
            t_data = {
                "collect": collect,
                "instance_id": targ.get("meta/instanceID"),
                "date": targ.get("date"),
                "debut": targ.get("debut"),
                "fin": targ.get("fin"),
                "actuelle_cercle": targ.get('adresse-mali/actuelle_cercle'),
                "actuelle_commune": targ.get('adresse-mali/actuelle_commune'),
                "actuelle_region": targ.get('adresse-mali/actuelle_region'),
                "actuelle_nom_generale_utilise": targ.get('adresse-mali/actuelle_nom_generale_utilise'),
                "metier_pays_prove": self.get_bol(targ.get('formation-experience/metier_pays_prove')),
                "suivi_formation": self.get_bol(targ.get('formation-experience/suivi_formation')),
                "beneficiez_lassistance": self.get_bol(targ.get('generales-chef-manage/beneficiez_lassistance')),
                "chef_age": targ.get('generales-chef-manage/chef_age'),
                "chef_ddn": targ.get('generales-chef-manage/chef_ddn'),
                "chef_doc": targ.get('generales-chef-manage/chef_doc'),
                "chef_etat_civil": targ.get('generales-chef-manage/chef_etat_civil'),
                "chef_nom": targ.get('generales-chef-manage/chef_nom'),
                "chef_prenom": targ.get('generales-chef-manage/chef_prenom'),
                "chef_profession": Activite.objects.get(slug=targ.get('generales-chef-manage/chef_profession')),
                "chef_sexe": targ.get('generales-chef-manage/chef_sexe'),
                "camp": Camp.objects.get(slug=targ.get('generales-chef-manage/pays-asile/camp')),
                "continent_asile": targ.get('generales-chef-manage/pays-asile/continent_asile'),
                "pays_asile": targ.get('generales-chef-manage/pays-asile/pays_asile'),
                "ville_asile": targ.get('generales-chef-manage/pays-asile/ville_asile'),
                "continent_naissance": targ.get('generales-chef-manage/pays-naissance/continent_naissance'),
                "lieu_naissance": targ.get('generales-chef-manage/pays-naissance/lieu_naissance'),
                "pays_naissance": targ.get('generales-chef-manage/pays-naissance/pays_naissance'),
                "nu_doc": targ.get('generales-chef-manage/nu_doc'),
                "num_progres_menage": targ.get('generales-chef-manage/num_progres_menage') or targ.get('generales-chef-manage/num_progres_menage_alg'),
                "point_de_entree": targ.get('generales-chef-manage/point_de_entree'),
                "date_arrivee": targ.get('generales/date_arrivee'),
                "date_entretien": targ.get('generales/date_entretien'),
                "nom_agent": targ.get('generales/nom_agent'),
                "nu_enregistrement": targ.get('generales/nu_enregistrement'),
                "site_engistrement": targ.get('generales/site_engistrement'),
                "nature_construction": targ.get('hebergement/nature_construction'),
                "type_hebergement": targ.get('hebergement/type_hebergement'),
                "lieu_cercle": targ.get('lieu-activite/lieu_cercle'),
                "lieu_commune": targ.get('lieu-activite/lieu_commune'),
                "lieu_qvf": targ.get('lieu-activite/lieu_qvf') or targ.get('lieu-activite/lieu_nom_generale_utilise'),
                "lieu_region": targ.get('lieu-activite/lieu_region'),
                "formation_socio_prof": self.get_bol(targ.get('reinsertion-prof/formation_socio_prof')),
                "membre_pays": self.get_bol(targ.get('membre_pays')),
                "nbre_membre_reste": targ.get('nbre_membre_reste'),
                "signature": targ.get('signature'),
                "tel": targ.get('tel'),
                "abris": self.get_bol(targ.get('abris')),
            }
            # print(t_data)
            if t_data.get("metier_pays_prove"):
                t_data.update({"exercice_secteur": targ.get(
                    'formation-experience/exercice_secteur')})
            if t_data.get("suivi_formation"):
                t_data.update({"domaine_formation": targ.get(
                    'formation-experience/domaine_formation')})
            if t_data.get("formation_socio_prof"):
                t_data.update({
                    "secteur_prof": self.get_or_other(targ.get('reinsertion-prof/secteur_prof')),
                    "projet_activite": self.get_bol(targ.get('reinsertion-prof/projet_activite')),
                })
                if t_data.get("projet_activite"):
                    t_data.update({
                        "souhait_activite": targ.get('reinsertion-prof/souhait_activite'),
                        "type_projet": targ.get('reinsertion-prof/type_projet')
                    })
            if t_data.get("abris"):
                t_data.update({
                    "nature_construction": targ.get('hebergement/nature_construction'),
                    "type_hebergement": targ.get('hebergement/type_hebergement')
                })

            identifier = t_data.get('num_progres_menage') or "{}-{}".format(target.instance_id, count_m)
            target, ok = Target.objects.update_or_create(identifier=identifier, defaults=t_data)
            if t_data.get("beneficiez_lassistance"):
                for typ in targ.get('generales-chef-manage/assistance/type_assistance').split():
                    if typ == OTHER:
                        typ = targ.get('generales-chef-manage/assistance/type_assistance_other')
                    t_assistance, status = TypeAssistance.objects.get_or_create(slug=typ)
                    type_tag = TargetTypeAssistance()
                    type_tag.target = target
                    type_tag.type_assistance = t_assistance
                    type_tag.save()
                for o in targ.get('generales-chef-manage/assistance/organisations').split():
                    og, status = Organization.objects.get_or_create(slug=o)
                    # print(og)
                    organ_targ = OrganizationTarget()
                    organ_targ.organization = og
                    organ_targ.target = target
                    organ_targ.save()
            persons = targ.get('info-generale-membres/membres')
            if not persons:
                print("Not person in menage")
                continue
            print("Beging person save ")
            count_m = 0
            for person in persons:
                # lien, ok = Lien.objects.get_or_create(slug=person.get('info-generale-membres/membres/membre_lien'))
                # print(lien)
                count_m += 1
                p_data = {
                    "target": target,
                    "membre_age": person.get('info-generale-membres/membres/membre_age'),
                    "membre_age_mois": person.get('info-generale-membres/membres/membre_age_mois'),
                    "membre_ddn": person.get('info-generale-membres/membres/membre_ddn'),
                    "membre_lien": Lien.objects.get_or_create(slug=person.get('info-generale-membres/membres/membre_lien'))[0],
                    "membre_nom": person.get('info-generale-membres/membres/membre_nom'),
                    "membre_prenom": person.get('info-generale-membres/membres/membre_prenom'),
                    "membre_scolaire": NiveauxScolaire.objects.get(slug=person.get('info-generale-membres/membres/membre_scolaire')),
                    "membre_sexe": person.get('info-generale-membres/membres/membre_sexe'),
                    "num_progres_individuel": person.get('info-generale-membres/membres/num_progres_individul'),
                    "vulnerable": self.get_bol(person.get('info-generale-membres/membres/vulnerable')),
                    "referer": self.get_bol(person.get('info-generale-membres/membres/etat-civil-non-dispo/referer')),
                    "cente_etat_civil": person.get('info-generale-membres/membres/etat-civil-non-dispo/cente_etat_civil'),
                    "partage_info_perso": self.get_bol(person.get('info-generale-membres/membres/etat-civil-non-dispo/partage_info_perso')),
                    "dispo_doc_etat_civil": self.get_bol(person.get('info-generale-membres/membres/dispo_doc_etat_civil'))
                }
                if p_data.get("referer"):
                    p_data.update({"a_qui": person.get('info-generale-membres/membres/etat-civil-non-dispo/a_qui')})
                if p_data.get("partage_info_perso"):
                    p_data.update({
                        "existe_centre_etat_civil": self.get_bol(person.get('info-generale-membres/membres/etat-civil-non-dispo/existe_centre_etat_civil')),
                        "niveau_education_pere": NiveauxScolaire.objects.get(slug=person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents/niveau_education_pere')),
                        "niveau_education_mere": NiveauxScolaire.objects.get(slug=person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents/niveau_education_mere')),
                        "nom_mere": person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents/nom_mere'),
                        "nom_pere": person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents/nom_pere'),
                        "prenom_mere": person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents/prenom_mere'),
                        "prenom_pere": person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents/prenom_pere'),
                        "profession_mere": Activite.objects.get(slug=person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents/profession_mere')),
                        "profession_pere": Activite.objects.get(slug=person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents/profession_pere')),
                        "profession": Activite.objects.get(slug=person.get('info-generale-membres/membres/etat-civil-non-dispo/profession')),
                        "naissance_cercle": person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/naissance_cercle'),
                        "naissance_commune": person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/naissance_commune'),
                        "naissance_region": person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/naissance_region'),
                        "year_ddn": person.get('info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/year_ddn'),
                        "au_moins_deux_temoins": self.get_bol(person.get('info-generale-membres/membres/etat-civil-non-dispo/au_moins_deux_temoins')),
                    })
                if p_data.get("dispo_doc_etat_civil"):
                    p_data.update({
                        "num_acte_naissance": person.get('info-generale-membres/membres/etat-civil-dispo/num_acte_naissance'),
                        "num_acte_mariage": person.get('info-generale-membres/membres/etat-civil-dispo/num_acte_mariage'),
                        "num_carte_nina": person.get('info-generale-membres/membres/etat-civil-dispo/num_carte_nina'),
                        "num_carte_identite_national": person.get('info-generale-membres/membres/etat-civil-dispo/num_carte_identite_national'),
                        "num_passeport": person.get('info-generale-membres/membres/etat-civil-dispo/num_passeport'),
                    })
                else:
                    p_data.update({
                        "raison_non_dispo": person.get(
                            'info-generale-membres/membres/etat-civil-non-dispo/raison_non_dispo')
                    })
                print('Saving ...')
                identifier = p_data.get('num_progres_individul') or "{}-{}".format(target.instance_id, count_m)
                pn, ok = Person.objects.update_or_create(
                    identifier=identifier, defaults=p_data)
                print("{} - {}".format(pn.membre_nom, pn.membre_prenom))
                if p_data.get("partage_info_perso"):
                    print("partage_info_perso ", person.get(
                        'info-generale-membres/membres/etat-civil-non-dispo/les_contacts'))
                    les_contacts = person.get('info-generale-membres/membres/etat-civil-non-dispo/les_contacts')
                    if les_contacts:
                        for ctt in les_contacts:
                            print(ctt)
                            data = {
                                "contact": ctt.get(
                                    'info-generale-membres/membres/etat-civil-non-dispo/les_contacts/contact_temoins'),
                                "person": pn,
                            }
                            contact_t, ok = ContactTemoin.objects.update_or_create(**data)

                if p_data.get("vulnerable"):
                    print("vulnerabilite ", person.get('info-generale-membres/membres/vulnerabilite'))
                    for vul in person.get('info-generale-membres/membres/vulnerabilite'):
                        if vul == OTHER:
                            vul = targ.get('info-generale-membres/membres/vulnerabilite_other')

                            vulnerabilite, status = Vulnerability.objects.get_or_create(slug=vul)
                            vul_person = VulnerabilityPerson()
                            vul_person.person = pn
                            vul_person.vulnerabily = vulnerabilite
