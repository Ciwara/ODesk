#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
# import os
from collections import OrderedDict
# import io
# import qrcode

from django.db import models
from django.utils import timezone
from jsonfield.fields import JSONField

# from hamed.identifiers import full_random_id
# from desk.utils import get_attachment, PERSONAL_FILES
# from hamed.ona import delete_submission

# from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# from desk.models import Entity, Provider

logger = logging.getLogger(__name__)


class ContactTemoin(models.Model):

    class Meta:

        unique_together = (('person', 'contact'),)
        ordering = ['person']

    contact = models.CharField(max_length=200)
    person = models.ForeignKey("Person", related_name='Contacts')

    def __str__(self):
        return "{person}.{contact}".format(
            person=self.person, contact=self.contact)


class VulnerabilityPerson(models.Model):

    class Meta:

        unique_together = (('person', 'vulnerability'),)
        ordering = ['person']

    vulnerability = models.ForeignKey(
        "vulnerability", related_name="vulnerabilities")
    person = models.ForeignKey("Person", related_name='vulnerability_persons')

    def __str__(self):
        return "{person}.{vulnerability}".format(
            person=self.person, vulnerability=self.vulnerability)


class Person(models.Model):

    class Meta:
        ordering = ['started_on', 'membre_nom', 'membre_prenom']

    MALE = 'masculin'
    FEMALE = 'feminin'
    GENDERS = OrderedDict([
        (MALE, "Masculin"),
        (FEMALE, "Feminin")
    ])
    SEXES = OrderedDict([
        (MALE, "Homme"),
        (FEMALE, "Femme")
    ])
    VRF = "vrf"
    D1 = "d1"
    D2 = "d2"
    DOC_ENREGISTREMENETS = OrderedDict([
        (VRF, "Formulaire de retour volontaire"),
        (D1, "Attestation de réfugier"),
        (D2, "Carte des ration"),
    ])
    PPF = "perte_pendant_la_fuite"
    PEA = "perte_en_asile"
    JE = "jamais_enregistre"
    RAISON_DOC_NON_DISPO = OrderedDict([
        (PPF, "Perte pendant la fuite "),
        (PEA, "Perte en asile"),
        (JE, " Jamais enregistré")
    ])

    O = "ong"
    M = "mairie"
    T = "trubinal"
    REFERENCE = OrderedDict([
        (O, "ONG"),
        (M, "Mairie"),
        (T, "Trubinal")
    ])
    AN = "acte-naissance"
    AM = "acte-mariage "
    NINA = "carte-nina"
    CIN = "carte-identite_national"
    PAS = "passeport"
    DOC_ETAT_CIVILs = OrderedDict([
        (AN, "Acte de naissante"),
        (AM, "Acte Mariage"),
        (NINA, "Carte NINA"),
        (CIN, "Carte d'identité nationale"),
        (PAS, "passeport")
    ])
    M = "mairie"
    C = "centre_secondire"
    J = "justice"
    CENTRE_ETAT_CIVIL = OrderedDict([
        (M, "Maire"),
        (C, "Centre Sécondaire D'Etat Civil"),
        (J, "Justice"),
    ])

    started_on = models.DateTimeField(default=timezone.now)
    identifier = models.CharField(max_length=10, primary_key=True)
    target = models.ForeignKey(
        'Target', related_name='targets')
    membre_nom = models.CharField(blank=True, null=True, max_length=100)
    membre_prenom = models.CharField(blank=True, null=True, max_length=100)
    membre_sexe = models.CharField(
        blank=True, null=True, choices=GENDERS.items(), max_length=20)
    membre_ddn = models.DateField(blank=True, null=True)
    membre_age = models.IntegerField(default=0)
    membre_age_mois = models.IntegerField(default=0, null=True)
    membre_lien = models.ForeignKey(
        "Lien", blank=True, null=True, max_length=100, related_name="liens")
    membre_scolaire = models.ForeignKey(
        'NiveauxScolaire', blank=True, null=True, related_name="membre_scolaires")
    num_progres_individuel = models.CharField(blank=True, null=True, max_length=100)
    vulnerable = models.BooleanField(default=False)
    dispo_doc_etat_civil = models.BooleanField(default=False)
    # info-etat-civil-dispo
    num_acte_naissance = models.CharField(blank=True, null=True, max_length=100)
    num_acte_mariage = models.CharField(blank=True, null=True, max_length=100)
    num_carte_nina = models.CharField(blank=True, null=True, max_length=100)
    num_carte_identite_national = models.CharField(
        blank=True, null=True, max_length=100)
    num_passeport = models.CharField(blank=True, null=True, max_length=100)
    # info-etat-civil-non-dispo
    raison_non_dispo = models.CharField(
        choices=RAISON_DOC_NON_DISPO.items(), max_length=50)
    partage_info_perso = models.BooleanField(default=False)
    # info-etablissement-docu
    year_ddn = models.IntegerField(blank=True, null=True)
    naissance_region = models.CharField(blank=True, null=True, max_length=100)
    naissance_cercle = models.CharField(blank=True, null=True, max_length=100)
    naissance_commune = models.CharField(blank=True, null=True, max_length=100)
    # info-parents
    nom_pere = models.CharField(blank=True, null=True, max_length=100)
    prenom_pere = models.CharField(blank=True, null=True, max_length=100)
    profession_pere = models.ForeignKey(
        'Activite', blank=True, null=True, related_name="professions_pere")
    niveau_education_pere = models.ForeignKey(
        'NiveauxScolaire', blank=True, null=True,
        related_name="niveaux_scolaires_pere")
    nom_mere = models.CharField(blank=True, null=True, max_length=100)
    prenom_mere = models.CharField(blank=True, null=True, max_length=100)
    profession_mere = models.ForeignKey(
        'Activite', blank=True, null=True, related_name="professions_mere")
    niveau_education_mere = models.ForeignKey(
        'NiveauxScolaire', blank=True, null=True,
        related_name="niveaux_scolaires_mere")
    profession = models.ForeignKey(
        'Activite', blank=True, null=True, related_name="professions")
    existe_centre_etat_civil = models.BooleanField(default=False)
    cente_etat_civil = models.CharField(
        blank=True, null=True, choices=CENTRE_ETAT_CIVIL.items(), max_length=100)
    au_moins_deux_temoins = models.BooleanField(default=False)
    referer = models.BooleanField(default=False)
    a_qui = models.CharField(choices=REFERENCE.items(), max_length=100)
    form_dataset = JSONField(default=dict, blank=True)

    def name(self):
        return "{}-{}".format(self.membre_nom, self.membre_prenom)

    def get_dentification(self):
        if self.num_progres_individuel:
            return self.num_progres_individuel
        else:
            return self.identifier

    def __str__(self):
        return self.name()
