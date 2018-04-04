#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

# from optparse import make_option
import glob
import json
from django.core.management.base import BaseCommand

from migrants.models import Survey, Person, Country
from desk.models import Entity


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            help='json file to import from',
            action='store',
            dest='input_file'
        )
        parser.add_argument(
            '-all',
            help='json file to import from',
            action='store',
            dest='folder'
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

        all_file = glob.glob('{}/*.json'.format(options.get('folder')))
        for json_file in all_file:
            self.setup(json_file)

    def setup(self, json_file):
        print("--"*50)
        print(json_file)
        print("--"*50)
        with open(json_file) as data_f:
            data = json.loads(data_f.read())
        for famille in data:
            sv = Survey()
            localite = famille.get("localite")
            print(localite)
            if not localite:
                localite = "90000000"

            sv.locality = Entity.objects.get(slug=localite)
            sv.instanceID = str(famille.get("instanceID"))
            sv.uuid = famille.get("uuid")
            sv.date = famille.get("date")
            sv.debut = famille.get("debut")
            sv.fin = famille.get("fin")
            sv.max_year = famille.get("max-year")
            sv.type_operation = famille.get("type-operation")
            sv.cause = famille.get("cause") or famille.get("cause-other")
            sv.nom_agent = famille.get("nom-agent")
            sv.date_arrivee = famille.get("date-arrivee")
            sv.date_ebtretien = famille.get("date-ebtretien")
            menage_pays_provenance = Country.get_or_create(
                slug=famille.get("menage-pays-provenance").lower(),
                name=famille.get("menage-pays-provenance"))
            sv.menage_pays_provenance = menage_pays_provenance
            sv.menage_ville = famille.get("menage-ville")
            sv.menage_point_entrer = famille.get("menage-point-entrer")
            sv.menage_doc_voyage = famille.get("menage-doc-voyage")
            sv.menage_numero_doc_voyage = famille.get("menage-numero-doc-voyage")
            sv.menage_bien_pays_provenance = self.get_bol(famille.get("menage-bien-pays-provenance", ""))
            sv.membre_pays_provenance = self.get_bol(famille.get("membre-pays-provenance"))
            nb_membre = famille.get("nb-membre")
            if nb_membre:
                nb_membre = int(famille.get("nb-membre"))
            sv.nb_membre = 0 if not nb_membre else int(nb_membre)
            sv.retour_rejoidre_famille = famille.get("reour-rejoidre-famille")
            sv.faire_venir_famille = famille.get("faire-venir-famille")
            sv.lieu_region = famille.get("lieu_region")
            sv.lieu_cercle = famille.get("lieu_cercle")
            sv.lieu_commune = famille.get("lieu_commune")
            sv.lieu_village_autre = famille.get("lieu_village_autre")
            sv.rue = str(famille.get("rue"))
            sv.porte = str(famille.get("porte"))
            sv.tel = famille.get("tel")
            sv.hebergement = famille.get('hebergement') or famille.get("hebergement_other")
            sv.bonne_sante = self.get_bol(famille.get("bonne-sante"))
            sv.maladie_chronique = str(famille.get("maladie-chronique")) or str(famille.get("maladie-chronique_other"))
            sv.prise_medicaments = str(famille.get("prise-medicaments"))
            sv.medicaments = str(famille.get("medicaments"))
            sv.fromation_pro = self.get_bol(famille.get("fromation-pro"))
            sv.domaine = famille.get("domaine")
            sv.metier = self.get_bol(famille.get("metier"))
            sv.secteur = famille.get("secteur")
            sv.f1 = self.get_bol(famille.get("f1", "non"))
            sv.f2 = famille.get("f2")
            sv.f3 = self.get_bol(famille.get("f3", "non"))
            sv.f4 = famille.get("f4")
            sv.f5 = famille.get("f5")
            sv.activite_region = str(famille.get("activite-region"))
            sv.activite_cercle = str(famille.get("activite-cercle"))
            sv.activite_commune = str(famille.get("activite-commune"))
            sv.activite_village_autre = str(famille.get("activite-village-autre"))
            sv.observations = str(famille.get("observations"))
            try:
                sv.menage_photo_doc_voyage_url_odk = str(famille.get(
                    "menage-photo-doc-voyage").get('url'))
            except Exception as e:
                print(e)
            sv.save()

            for membre in famille.get('membre-menage'):
                mmb = Person()
                mmb.survey = sv
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
                    mmb.ddn = ddn
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
                print("{} {}".format("*" * 30, membre.get("membre-vulnerabilite")))
                mmb.membre_vul1 = membre.get("membre-vul1")
                mmb.membre_vul2 = membre.get("membre-vul2")
                mmb.membre_vul3 = membre.get("membre-vul3")
                try:
                    mmb.membre_photo_url_odk = membre.get(
                        "photo-membre").get('url')
                except Exception as e:
                    print(e)
                try:
                    mmb.save()
                except Exception as e:
                    print(e)
                print("NOM :", mmb)
