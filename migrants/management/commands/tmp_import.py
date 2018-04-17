#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import datetime
import json
from django.core.management.base import BaseCommand

from migrants.models import Survey, Person, Country
from desk.models import Entity


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            help='json file to import from',
            action='store',
            dest='add_survey'
        )
        parser.add_argument(
            '-m',
            help='json file to import from',
            action='store',
            dest='add_menage'
        )

    def date_format(self, strdate):
        return datetime.datetime.strptime(strdate, '%b %d, %Y')

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
        survey = options.get('add_survey')
        menage = options.get('add_menage')
        print("-- " * 50)
        with open(survey) as data_f:
            self.s_data = json.loads(data_f.read())
        with open(menage) as data_f:
            self.m_data = json.loads(data_f.read())

        for membre in self.m_data:
            mmb = Person()
            mmb.nationalite = membre.get("membre-nationalite")
            mmb.prenoms = membre.get("membre-prenoms")
            mmb.nom = membre.get("membre-nom")
            mmb.gender = self.get_sex(membre.get("membre-sexe"))
            mmb.type_naissance = membre.get("membre-type-naissance")
            annee_naissance = membre.get("membre-annee-naissance")
            if annee_naissance:
                mmb.annee_naissance = int(annee_naissance)
            ddn = membre.get("membre-ddn")
            if ddn:
                mmb.ddn = self.date_format(ddn)
            mmb.age = membre.get("membre-age") or membre.get("membre-age1")
            mmb.profession = membre.get("membre-profession") or membre.get("membre-profession_other")
            mmb.etat_civil = self.get_etat_civil(membre.get("membre-etat-civil"))
            mmb.lien = membre.get("membre-lien")
            mmb.niveau_scolaire = membre.get("membre-niveau-scolaire")
            mmb.document = membre.get("membre-document")
            mmb.num_doc = membre.get("membre-num-doc")
            mmb.nina = membre.get("membre-nina")
            mmb.biometric = membre.get("membre-biometric")
            mmb.saisie_nina = membre.get("saisie-nina")
            mmb.saisie_biometric = membre.get("saisie-biometric")
            mmb.membre_vulnerabilite = self.get_bol(
                membre.get("membre-vulnerabilite"))
            mmb.membre_vul1 = membre.get("membre-vul1")
            mmb.membre_vul2 = membre.get("membre-vul2")
            mmb.membre_vul3 = membre.get("membre-vul3")
            try:
                mmb.membre_photo_url_odk = membre.get(
                    "photo-membre")
            except Exception as e:
                print("membre_photo_url_odk", e)
            try:
                mmb.survey = Survey.objects.get(instanceID=membre.get("PARENT_KEY"))
            except Exception as e:
                print("No exite", e)
                mmb.survey = self.create_survey(membre.get("PARENT_KEY"))
            try:
                mmb.save()
            except Exception as e:
                print("mmb", e)
            print("NOM :", mmb)

    def create_survey(self, pkey):

        for famille in self.s_data:
            # print(famille.get("SubmissionDate"))
            if famille.get("KEY") == pkey:
                print("{} == {}".format(pkey, famille.get("meta-instanceID")))
                sv = Survey()
                localite = famille.get("localite")
                # print(localite)
                if not localite:
                    localite = "90000000"

                sv.locality = Entity.objects.get(slug=localite)
                sv.instanceID = str(famille.get("meta-instanceID"))
                sv.uuid = famille.get("formhub-uuid")
                sv.date = self.datetime_format(famille.get("SubmissionDate"))
                sv.debut = self.datetime_format(famille.get("debut"))
                sv.fin = self.datetime_format(famille.get("fin"))
                sv.max_year = famille.get("max_year")
                sv.type_operation = famille.get("operation-repatriement-type-operation")
                sv.cause = famille.get("operation-repatriement-cause") or famille.get("operation-repatriement-cause-other")
                sv.nom_agent = famille.get("operation-repatriement-nom-agent")
                sv.date_arrivee = self.date_format(
                    famille.get("operation-repatriement-date-arrivee"))
                sv.date_ebtretien = self.date_format(
                    famille.get("operation-repatriement-date-ebtretien"))
                menage_pays_provenance = Country.get_or_create(
                    slug=famille.get("informations-generales-menage-menage-pays-provenance").lower(),
                    name=famille.get("informations-generales-menage-menage-pays-provenance"))
                sv.menage_pays_provenance = menage_pays_provenance
                sv.menage_ville = famille.get("informations-generales-menage-menage-ville")
                sv.menage_point_entrer = famille.get("informations-generales-menage-menage-point-entrer")
                sv.menage_doc_voyage = famille.get("informations-generales-menage-menage-doc-voyage")
                sv.menage_numero_doc_voyage = famille.get(
                    "informations-generales-menage-menage-numero-doc-voyage")
                sv.menage_bien_pays_provenance = self.get_bol(
                    famille.get("informations-generales-menage-menage-bien-pays-provenance", ""))
                sv.membre_pays_provenance = self.get_bol(
                    famille.get("informations-generales-menage-membre-pays-provenance"))
                nb_membre = famille.get("informations-generales-menage-nb-membre")
                if nb_membre:
                    nb_membre = int(nb_membre)
                sv.nb_membre = 0 if not nb_membre else int(nb_membre)
                sv.retour_rejoidre_famille = famille.get("informations-generales-menage-reour-rejoidre-famille")
                sv.faire_venir_famille = self.get_bol(famille.get("informations-generales-menage-faire-venir-famille"))
                sv.lieu_region = famille.get("adresse-mali-lieu_region")
                sv.lieu_cercle = famille.get("adresse-mali-lieu_cercle")
                sv.lieu_commune = famille.get("adresse-mali-lieu_commune")
                sv.lieu_village_autre = famille.get("lieu_village_autre")
                sv.rue = str(famille.get("adresse-mali-rue"))
                sv.porte = str(famille.get("adresse-mali-porte"))
                sv.tel = famille.get("adresse-mali-tel")
                sv.hebergement = famille.get('type-hebergement-hebergement') or famille.get(
                    "type-hebergement-hebergement_other")
                sv.bonne_sante = self.get_bol(famille.get("sante-appui-bonne-sante"))
                sv.maladie_chronique = str(famille.get(
                    "sante-appui-maladie-chronique")) or str(famille.get(
                        "sante-appui-maladie-chronique_other"))
                sv.prise_medicaments = str(famille.get("sante-appui-prise-medicaments"))
                sv.medicaments = str(famille.get("sante-appui-medicaments"))
                sv.fromation_pro = self.get_bol(famille.get("formation-experience-fromation-pro"))
                sv.domaine = famille.get("formation-experience-domaine")
                sv.metier = self.get_bol(famille.get("formation-experience-metier"))
                sv.secteur = famille.get("formation-experience-secteur")
                sv.f1 = self.get_bol(famille.get("reinsertion-professionnelle-F1", "non"))
                sv.f2 = famille.get("reinsertion-professionnelle-F2")
                sv.f3 = self.get_bol(famille.get("reinsertion-professionnelle-F3", "non"))
                sv.f4 = famille.get("reinsertion-professionnelle-F4")
                sv.f5 = famille.get("reinsertion-professionnelle-F5")
                sv.activite_region = str(famille.get(
                    "reinsertion-professionnelle-F6-activite_region"))
                sv.activite_cercle = str(famille.get(
                    "reinsertion-professionnelle-F6-activite_cercle"))
                sv.activite_commune = str(famille.get(
                    "reinsertion-professionnelle-F6-activite_commune"))
                sv.activite_village_autre = str(famille.get(
                    "reinsertion-professionnelle-F6-activite_village_autre"))
                sv.observations = str(famille.get("observations"))
                try:
                    sv.menage_photo_doc_voyage_url_odk = str(famille.get(
                        "informations-generales-menage-menage-photo-doc-voyage"))
                except Exception as e:
                    print("menage_photo_doc_voyage_url_odk", e)
                sv.save()
