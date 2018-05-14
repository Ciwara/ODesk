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
    TargetTypeAssistance, OrganizationTarget, Collect, Target,
    Person, ContactTemoin, VulnerabilityPerson)

from desk.models import Provider, RegistrationSite
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
        if not value:
            "{}_other".format(value)
        return value

    def get_with_other(self, value):
        if not value:
            "{}_other".format(value)
        return value

    def setup(self):
        self.get_save_target()

    def get_save_target(self):

        collect = Collect.objects.get(name="Formulaire rapatiment")
        rdata = get_form_data(collect.ona_form_pk)
        for targ in rdata:
            try:
                site_engistrement = RegistrationSite.objects.get(
                    slug=targ.get('generales/site_engistrement'))
            except Exception as e:
                print("Creating SITE")
                site_engistrement = RegistrationSite()
                site_engistrement.slug = targ.get('generales/site_engistrement')
                site_engistrement.name = targ.get('generales/site_engistrement')
                site_engistrement.confirmed = False
                site_engistrement.save()

            t_data = {
                "collect": collect,
                "date": targ.get("date"),
                "debut": targ.get("debut"),
                "fin": targ.get("fin"),
                "nom_agent": targ.get("generales/nom_agent"),
                "nu_enregistrement": targ.get("generales/nu_enregistrement"),
                "site_engistrement": site_engistrement,
                "date_arrivee": targ.get("generales/date_arrivee"),
                "date_entretien": targ.get("generales/date_entretien"),
                "continent_asile": targ.get("info-generales-manage/pays-asile/continent_asile"),
                "pays_asile": targ.get("info-generales-manage/pays-asile/pays_asile"),
                "ville_asile": targ.get("info-generales-manage/pays-asile/ville_asile"),
                "camp": targ.get("info-generales-manage/pays-asile/camp"),
                "camp_other": targ.get("info-generales-manage/pays-asile/camp_other"),
                "num_progres_menage_alg": targ.get("info-generales-manage/num_progres_menage_alg"),
                "num_progres_menage": targ.get("info-generales-manage/num_progres_menage"),
                "point_de_entree": targ.get("info-generales-manage/point_de_entree"),
                "continent_naissance": targ.get("info-generales-manage/pays-naissance/continent_naissance"),
                "pays_naissance": targ.get("info-generales-manage/pays-naissance/pays_naissance"),
                "lieu_naissance": targ.get("info-generales-manage/pays-naissance/lieu_naissance"),
                "chef_etat_civil": targ.get("info-generales-manage/chef_etat_civil"),
                "chef_profession": targ.get("info-generales-manage/chef_profession"),
                "chef_doc": targ.get("info-generales-manage/chef_doc"),
                "num_doc": targ.get("info-generales-manage/num_doc"),
                "beneficiez_lassistance": self.get_bol(targ.get("info-generales-manage/assistance/beneficiez_lassistance")),
                "actuelle_region": targ.get("adresse-mali/actuelle_region"),
                "actuelle_cercle": targ.get("adresse-mali/actuelle_cercle"),
                "actuelle_commune": targ.get("adresse-mali/actuelle_commune"),
                "actuelle_qvf": targ.get("adresse-mali/actuelle_qvf"),
                "actuelle_nom_generale_utilise": targ.get("adresse-mali/actuelle_nom_generale_utilise"),
                "rue": targ.get("adresse-mali/rue"),
                "porte": targ.get("adresse-mali/porte"),
                "tel": targ.get("adresse-mali/tel"),

                "abris": self.get_bol(targ.get("hebergement/abris")),
                "nature_construction": targ.get("hebergement/nature_construction"),
                "nature_construction_other": targ.get("hebergement/nature_construction_other"),
                "type_hebergement": targ.get("hebergement/type_hebergement"),
                "type_hebergement_other": targ.get("hebergement/type_hebergement_other"),

                "membre_pays": self.get_bol(targ.get("info-generale-membres/membre_pays")),
                "nbre_membre_reste": targ.get("info-generale-membres/nbre_membre_reste"),
                "etat_sante": self.get_bol(targ.get("sante-appuipyschosocial/etat_sante")),
                "situation_maladie": targ.get("sante-appuipyschosocial/situation_maladie"),
                "type_maladie": targ.get("sante-appuipyschosocial/type_maladie"),
                "type_maladie_other": targ.get("sante-appuipyschosocial/type_maladie_other"),
                "type_aigue": targ.get("sante-appuipyschosocial/type_aigue"),
                "type_aigue_other": targ.get("sante-appuipyschosocial/type_aigue_other"),
                "prise_medicament": targ.get("sante-appuipyschosocial/prise_medicament"),
                "type_medicaments": targ.get("sante-appuipyschosocial/type_medicaments"),

                "suivi_formation": self.get_bol(targ.get("formation-experience/suivi_formation")),
                "domaine_formation": targ.get("formation-experience/domaine_formation"),

                "metier_pays_prove": self.get_bol(targ.get("formation-experience/metier_pays_prove")),
                "exercice_secteur": targ.get("formation-experience/exercice_secteur"),
                "exercice_secteur_other": targ.get("formation-experience/exercice_secteur_other"),

                "formation_socio_prof": self.get_bol(targ.get("reinsertion-prof/formation_socio_prof")),
                "secteur_prof": targ.get("reinsertion-prof/secteur_prof"),
                "secteur_prof_other": targ.get("reinsertion-prof/secteur_prof_other"),

                "projet_activite": self.get_bol(targ.get('reinsertion-prof/projet_activite')),
                "type_projet": targ.get("reinsertion-prof/type_projet"),
                "souhait_activite": targ.get("reinsertion-prof/souhait_activite"),
                "souhait_activite_other": targ.get("reinsertion-prof/souhait_activite_other"),

                "lieu_region": targ.get("reinsertion-prof/lieu-activite/lieu_region"),
                "lieu_cercle": targ.get("reinsertion-prof/lieu-activite/lieu_cercle"),
                "lieu_commune": targ.get("reinsertion-prof/lieu-activite/lieu_commune"),
                "lieu_qvf": targ.get("reinsertion-prof/lieu-activite/lieu_qvf"),
                "lieu_non_generale_utilise": targ.get("reinsertion-prof/lieu-activite/lieu_non_generale_utilise"),
                "signature": targ.get("signature"),
            }
            target, ok = Target.objects.get_or_create(
                instance_id=targ.get("meta/instanceID"), defaults=t_data)
            if not ok:
                continue

            if t_data.get("beneficiez_lassistance"):
                for typ_assis in targ.get('info-generales-manage/assistance/type_assistance').split():
                    data = {
                        "target": target,
                        "type_assistance": typ_assis if typ_assis != OTHER else targ.get('info-generales-manage/assistance/type_assistance_other')
                    }
                    targ_typ, c = TargetTypeAssistance.objects.update_or_create(**data)
                for o in targ.get('info-generales-manage/assistance/organisations').split():
                    data = {
                        "target": target,
                        "organization": o if o != OTHER else targ.get('info-generales-manage/assistance/organisations_other')
                    }
                    organ_targ, c = OrganizationTarget.objects.update_or_create(**data)
            data_members = targ.get('info-generale-membres/membres')
            if not data_members:
                continue
            for person in data_members:
                p_data = {
                    "target": target,
                    "membre_nom": person.get("info-generale-membres/membres/membre_nom"),
                    "membre_prenom": person.get("info-generale-membres/membres/membre_prenom"),
                    "membre_sexe": person.get("info-generale-membres/membres/membre_sexe"),
                    "membre_ddn": person.get("info-generale-membres/membres/membre_ddn"),
                    "membre_age": person.get("info-generale-membres/membres/membre_age"),
                    "membre_age_mois": person.get("info-generale-membres/membres/membre_age_mois"),
                    "membre_lien": person.get("info-generale-membres/membres/membre_lien"),
                    "membre_scolaire": person.get("info-generale-membres/membres/membre_scolaire"),
                    "num_progres_individuel": person.get("info-generale-membres/membres/num_progres_individul"),
                    "membre_vulnerabilite": self.get_bol(person.get("info-generale-membres/membres/membre-vulnerabilite")),
                    "dispo_doc_etat_civil": self.get_bol(person.get("info-generale-membres/membres/dispo_doc_etat_civil")),
                    "partage_info_perso": self.get_bol(person.get("info-generale-membres/membres/etat-civil-non-dispo/partage_info_perso")),
                    "referer": self.get_bol(person.get("info-generale-membres/membres/etat-civil-non-dispo/referer")),
                    "a_qui": person.get('info-generale-membres/membres/etat-civil-non-dispo/a_qui'),
                    "a_qui_other": person.get("info-generale-membres/membres/etat-civil-non-dispo/a_qui_other"),
                    "naissance_region": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/naissance_region"),
                    "naissance_cercle": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/naissance_cercle"),
                    "naissance_commune": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/naissance_commune"),
                    "nom_pere": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents_p/nom_pere"),
                    "prenom_pere": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents_p/prenom_pere"),
                    "profession_pere": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents_p/profession_pere"),
                    "niveau_education_pere": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents_p/niveau_education_pere"),
                    "nom_mere": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents_m/nom_mere"),
                    "prenom_mere": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents_m/prenom_mere"),
                    "profession_mere": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents_m/profession_mere"),
                    "niveau_education_mere": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/parents_m/niveau_education_mere"),
                    "profession": person.get("info-generale-membres/membres/etat-civil-non-dispo/etablissement-docu/profession"),
                    "existe_centre_etat_civil": self.get_bol(person.get("info-generale-membres/membres/etat-civil-non-dispo/existe_centre_etat_civil")),
                    "centre_etat_civil": person.get("info-generale-membres/membres/etat-civil-non-dispo/centre_etat_civil"),
                    "centre_etat_civil_other": person.get("info-generale-membres/membres/etat-civil-non-dispo/centre_etat_civil_other"),
                    "au_moins_deux_temoins": self.get_bol(person.get("info-generale-membres/membres/etat-civil-non-dispo/au_moins_deux_temoins")),
                    "num_acte_naissance": person.get("info-generale-membres/membres/etat-civil-dispo/num_acte_naissance"),
                    "num_acte_mariage": person.get("info-generale-membres/membres/etat-civil-dispo/num_acte_mariage"),
                    "num_carte_nina": person.get("info-generale-membres/membres/etat-civil-dispo/num_carte_nina"),
                    "num_carte_identite_national": person.get("info-generale-membres/membres/etat-civil-dispo/num_carte_identite_national"),
                    "num_passeport": person.get("info-generale-membres/membres/etat-civil-dispo/num_passeport"),
                    "raison_non_dispo": person.get("info-generale-membres/membres/etat-civil-non-dispo/raison_non_dispo"),
                    "raison_non_dispo_other": person.get("info-generale-membres/membres/etat-civil-non-dispo/raison_non_dispo_other"),
                }
                pn, ok = Person.objects.update_or_create(**p_data)
                les_contacts = person.get('info-generale-membres/membres/etat-civil-non-dispo/les_contacts')
                if les_contacts:
                    for ctt in les_contacts:
                        data = {
                            "contact": ctt.get(
                                'info-generale-membres/membres/etat-civil-non-dispo/les_contacts/contact_temoins'),
                            "person": pn,
                        }
                        contact_t, ok = ContactTemoin.objects.update_or_create(**data)
                if person.get('info-generale-membres/membres/besoin-specifique'):
                    for dic_vul in person.get('info-generale-membres/membres/besoin-specifique'):
                        vul = dic_vul.get('info-generale-membres/membres/besoin-specifique/besoin_specifique')
                        subvul = dic_vul.get('info-generale-membres/membres/besoin-specifique/sub_besoin')
                    data = {
                        "person": pn,
                        "besoin_specifique": subvul,
                        "sub_besoin": vul
                    }
                    targ_typ, c = VulnerabilityPerson.objects.update_or_create(**data)
