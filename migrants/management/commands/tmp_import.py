#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import datetime
import json
import kronos

from django.core.management.base import BaseCommand
from django.core.management import call_command

from migrants.models import Survey, Person, Country
from desk.models import Entity
from odkextractor.models import FormID


@kronos.register('* * * * * *')
class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-u',
            help='json file to import from',
            action='store',
            dest='update_odk'
        )

    def date_format(self, strdate):
        date_ = datetime.datetime.strptime(strdate, '%b %d, %Y')
        # print(date_)
        return date_

    def datetime_format(self, strdatetime):
        return datetime.datetime.strptime(strdatetime, '%b %d, %Y %H:%M:%S %p')

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
        # print(options.get('update_odk'))
        if not options.get('update_odk'):
            print(u"odk_update_b_storage")
            call_command("odk_update_b_storage")
        for form in FormID.objects.filter(active=True):
            self.setup(form)

    def setup(self, form):

        # print("form_id : {}".format(form.form_id))
        with open(form.data_info_g_json) as data_f:
            m_data = json.loads(data_f.read())

        with open(form.data_json) as data_f:
            self.s_data = json.loads(data_f.read())

        for membre in m_data:
            # mmb = Person()
            data_mb = {
                'key_odk': membre.get("KEY"),
                'nationalite': membre.get("membre-nationalite"),
                'prenoms': membre.get("membre-prenoms"),
                'nom': membre.get("membre-nom"),
                'gender': self.get_sex(membre.get("membre-sexe")),
                'type_naissance': membre.get("membre-type-naissance"),
                'annee_naissance': None if not membre.get("membre-annee-naissance") else int(membre.get("membre-annee-naissance")),
                'ddn': None if not membre.get("membre-ddn") else self.date_format(membre.get("membre-ddn")),
                'age': membre.get("membre-age") or membre.get("membre-age1"),
                'profession': membre.get("membre-profession"),
                'profession_other': membre.get("membre-profession_other"),
                'etat_civil': self.get_etat_civil(membre.get("membre-etat-civil")),
                'lien': membre.get("membre-lien"),
                'niveau_scolaire': membre.get("membre-niveau-scolaire"),
                'document': membre.get("membre-document"),
                'num_doc': membre.get("membre-num-doc"),
                'nina': membre.get("membre-nina"),
                'biometric': membre.get("membre-biometric"),
                'saisie_nina': membre.get("saisie-nina"),
                'saisie_biometric': membre.get("saisie-biometric"),
                'membre_vulnerabilite': self.get_bol(membre.get("membre-vulnerabilite")),
                'membre_vul1': membre.get("membre-vul1"),
                'membre_vul2': membre.get("membre-vul2"),
                'membre_vul3': membre.get("membre-vul3"),
                'membre_photo': membre.get("photo-membre")
            }

            survey, created = self.create_survey(membre.get("PARENT_KEY"))
            data_mb.update({'survey': survey})
            try:
                person = Person.objects.get_or_create(key_odk=str(membre.get("KEY")), defaults=data_mb)
            except Exception as e:
                print("mmb", e)
            print("NOM :", person)

    def create_survey(self, pkey):

        for sv in self.s_data:
            # print(famille.get("SubmissionDate"))
            if sv.get("KEY") == pkey:
                # print("{} == {}".format(pkey, sv.get("meta-instanceID")))
                # localite = sv.get("localite")
                # # print(localite)
                # if not localite:
                #     localite = "90000000"
                data_sv = {
                    'formhub_uuid': sv.get("formhub-uuid"),
                    'submission_date': self.datetime_format(sv.get("SubmissionDate")),
                    'date_debut': self.datetime_format(sv.get("debut")),
                    'date_fin': self.datetime_format(sv.get("fin")),
                    'type_operation': sv.get("operation-repatriement-type-operation"),
                    'cause': sv.get("operation-repatriement-cause"),
                    'cause_other': sv.get("operation-repatriement-cause_other"),
                    'nom_agent': sv.get("operation-repatriement-nom-agent"),
                    'date_arrivee': self.date_format(sv.get("operation-repatriement-date-arrivee")),
                    'date_entretien': self.date_format(sv.get("operation-repatriement-date-ebtretien")),
                    'menage_pays_provenance': Country.get_or_create(
                        slug=sv.get("informations-generales-menage-menage-pays-provenance").lower(),
                        name=sv.get("informations-generales-menage-menage-pays-provenance")),
                    'menage_pays_de_provenance_ville': sv.get("informations-generales-menage-menage-ville"),
                    'menage_point_entrer': sv.get("informations-generales-menage-menage-point-entrer"),
                    'menage_doc_voyage': sv.get("informations-generales-menage-menage-doc-voyage"),
                    'menage_numero_doc_voyage': sv.get("informations-generales-menage-menage-numero-doc-voyage"),
                    'menage_bien_pays_provenance': self.get_bol(sv.get("informations-generales-menage-menage-bien-pays-provenance", "")),
                    'membre_pays_provenance': self.get_bol(sv.get("informations-generales-menage-membre-pays-provenance")),
                    'nb_membre': 0 if not sv.get("informations-generales-menage-nb-membre") else int(sv.get("informations-generales-menage-nb-membre")),
                    'retour_rejoidre_famille': self.get_bol(sv.get("informations-generales-menage-reour-rejoidre-famille")),
                    'faire_venir_famille': self.get_bol(sv.get("informations-generales-menage-faire-venir-famille")),
                    'adresse_mali_lieu_region': sv.get("adresse-mali-lieu_region"),
                    'adresse_mali_lieu_cercle': sv.get("adresse-mali-lieu_cercle"),
                    'adresse_mali_lieu_commune': sv.get("adresse-mali-lieu_commune"),
                    'adresse_mali_lieu_village_autre': sv.get("lieu_village_autre"),
                    'rue': str(sv.get("adresse-mali-rue")),
                    'porte': str(sv.get("adresse-mali-porte")),
                    'tel': sv.get("adresse-mali-tel"),
                    'hebergement': sv.get('type-hebergement-hebergement'),
                    'hebergement_other': sv.get("type-hebergement-hebergement_other"),
                    'bonne_sante': self.get_bol(sv.get("sante-appui-bonne-sante")),
                    'maladie_chronique': str(sv.get("sante-appui-maladie-chronique")),
                    'maladie_chronique_other': str(sv.get("sante-appui-maladie-chronique_other")),
                    'prise_medicaments': str(sv.get("sante-appui-prise-medicaments")),
                    'medicaments': str(sv.get("sante-appui-medicaments")),
                    'fromation_pro': self.get_bol(sv.get("formation-experience-fromation-pro")),
                    'domaine': sv.get("formation-experience-domaine"),
                    'metier': self.get_bol(sv.get("formation-experience-metier")),
                    'formation_experience_secteur': sv.get("formation-experience-secteur"),
                    'reinsertion_professionnelle_f1': self.get_bol(sv.get("reinsertion-professionnelle-F1", "non")),
                    'reinsertion_professionnelle_f2': sv.get("reinsertion-professionnelle-F2"),
                    'reinsertion_professionnelle_f3': self.get_bol(sv.get("reinsertion-professionnelle-F3", "non")),
                    'reinsertion_professionnelle_f4': sv.get("reinsertion-professionnelle-F4"),
                    'reinsertion_professionnelle_f5': sv.get("reinsertion-professionnelle-F5"),
                    'reinsertion_professionnelle_f6_activite_region': str(sv.get("reinsertion-professionnelle-F6-activite_region")),
                    'reinsertion_professionnelle_f6_activite_cercle': str(sv.get("reinsertion-professionnelle-F6-activite_cercle")),
                    'reinsertion_professionnelle_f6_activite_commune': str(sv.get("reinsertion-professionnelle-F6-activite_commune")),
                    'reinsertion_professionnelle_f6_activite_village_autre': str(sv.get("reinsertion-professionnelle-F6-activite_village_autre")),
                    'observations': str(sv.get("observations")),
                    'menage_photo_doc_voyage': sv.get("informations-generales-menage-menage-photo-doc-voyage")
                }
                return Survey.objects.get_or_create(instance_id=str(sv.get("meta-instanceID")), defaults=data_sv)
