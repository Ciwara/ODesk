#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
# import os
from collections import OrderedDict
import io
import qrcode
from django.db import models
from django.utils import timezone
# from django.conf import settings
from jsonfield.fields import JSONField
from django.urls import reverse

# from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from repatriate.person_checks import (
    no_doc_with_num_pi, requise_num_progres_individuel, invalide_num_progres_individuel)

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

        unique_together = (('person', 'sub_besoin'),)
        ordering = ['person']

    besoin_specifique = models.CharField(blank=True, null=True, max_length=100)
    sub_besoin = models.CharField(blank=True, null=True, max_length=100)
    person = models.ForeignKey("Person", related_name='vulnerability_persons')

    def __str__(self):
        return "{person}.{besoin_specifique} {sub_besoin}".format(
            person=self.person, besoin_specifique=self.besoin_specifique,
            sub_besoin=self.sub_besoin)


class PersonManager(models.Manager):
    def get_queryset(self):
        return super(PersonManager, self).get_queryset().filter(deleted=False)


class Person(models.Model):

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
    VRF = "formulaire_de_retour_volontaire"
    D1 = "attestation_de_refugie"
    D2 = "carte_des_ration"
    SD = "sans_doc"

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

    U = "1"
    D = "2"
    T = "3"
    Q = "4"
    C = "5"
    S = "6"
    ST = "7"
    H = "8"
    N = "9"
    DX = "10"
    O = "11"
    DS = "12"
    TZ = "13"
    TC = "TC"
    UG = "UG"
    PG = "PG"
    IN = "IN"
    NE = "NE"
    U = "U"
    Niveau = OrderedDict([
        (U, "1ère année d'études"),
        (D, "2 ère année d'études"),
        (T, "3 ère année d'études"),
        (Q, "4 ère année d'études"),
        (C, "5 ère année d'études"),
        (S, "6 ère année d'études"),
        (ST, "7 ère année d'études"),
        (H, "8 ère année d'études"),
        (N, "9 ère année d'études"),
        (DX, "Secondaire 1"),
        (O, "Secondaire 2"),
        (DS, "Secondaire 3"),
        (TZ, "Professionnel/ Agriculture"),
        (TC, "Technique ou Bénévole"),
        (UG, "Niveau Universitaire"),
        (PG, "Second cycle/ Doctorat"),
        (IN, "Education informelle"),
        (NE, "Aucune éducation"),
        (U, "Inconnue")])

    class Meta:
        unique_together = (('identifier'),)
        ordering = ['started_on', 'membre_nom', 'membre_prenom']

    started_on = models.DateTimeField(default=timezone.now)
    identifier = models.CharField(max_length=15, primary_key=True)
    target = models.ForeignKey('Target', related_name='targets')
    membre_nom = models.CharField(blank=True, null=True, max_length=100)
    membre_prenom = models.CharField(blank=True, null=True, max_length=100)
    membre_sexe = models.CharField(
        blank=True, null=True, choices=GENDERS.items(), max_length=20)
    membre_ddn = models.DateField(blank=True, null=True)
    membre_age = models.IntegerField(default=0)
    membre_age_mois = models.IntegerField(default=0, null=True, blank=True)
    membre_lien = models.CharField(blank=True, null=True, max_length=100)
    membre_scolaire = models.CharField(
        "Niveau scolaire", choices=Niveau.items(), blank=True, null=True, max_length=100)
    num_progres_individuel = models.CharField(blank=True, null=True, max_length=100)
    membre_vulnerabilite = models.BooleanField(default=False)
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
        null=True, blank=True, choices=RAISON_DOC_NON_DISPO.items(), max_length=50)
    raison_non_dispo_other = models.CharField(
        blank=True, null=True, max_length=100)
    partage_info_perso = models.BooleanField(default=False)
    # info-etablissement-docu
    # year_ddn = models.IntegerField(blank=True, null=True)
    naissance_region = models.CharField(blank=True, null=True, max_length=100)
    naissance_cercle = models.CharField(blank=True, null=True, max_length=100)
    naissance_commune = models.CharField(blank=True, null=True, max_length=100)
    # info-parents
    nom_pere = models.CharField(blank=True, null=True, max_length=100)
    prenom_pere = models.CharField(blank=True, null=True, max_length=100)
    profession_pere = models.CharField(blank=True, null=True, max_length=100)
    niveau_education_pere = models.CharField(
        choices=Niveau.items(), blank=True, null=True, max_length=100)
    nom_mere = models.CharField(blank=True, null=True, max_length=100)
    prenom_mere = models.CharField(blank=True, null=True, max_length=100)
    profession_mere = models.CharField(blank=True, null=True, max_length=100)
    niveau_education_mere = models.CharField(
        choices=Niveau.items(), blank=True, null=True, max_length=100)
    profession = models.CharField(blank=True, null=True, max_length=100)
    existe_centre_etat_civil = models.BooleanField(default=False)
    centre_etat_civil = models.CharField(
        blank=True, null=True, choices=CENTRE_ETAT_CIVIL.items(), max_length=100)
    centre_etat_civil_other = models.CharField(blank=True, null=True, max_length=100)
    au_moins_deux_temoins = models.BooleanField(default=False)
    referer = models.BooleanField(default=False)
    a_qui = models.CharField(
        blank=True, null=True, choices=REFERENCE.items(), max_length=100)
    a_qui_other = models.CharField(null=True, blank=True, max_length=50)
    form_dataset = JSONField(default=dict, blank=True)
    deleted = models.BooleanField(default=False)

    # Checks
    is_invalide_num_pi = models.BooleanField(default=True)
    is_requise_num_progres_individuel = models.BooleanField(default=True)
    is_not_empty_num_pi_alg = models.BooleanField(default=True)
    is_vrf_wihtout_num_pi = models.BooleanField(default=True)
    is_sans_doc_avec_num_pi = models.BooleanField(default=True)
    is_num_pi_sans_num_pm = models.BooleanField(default=True)
    is_doublon_pm_pi = models.BooleanField(default=True)

    objects = models.Manager() # The default manager.
    active_objects = PersonManager()

    def name(self):
        return "{}-{}-{}-{}".format(
            self.identifier, self.membre_nom, self.membre_prenom, self.membre_sexe)

    def get_absolute_url(self):
        return reverse('correction_person', kwargs={'id': self.identifier})

    def les_temoins(self):
        return ContactTemoin.objects.filter(person=self).all()

    @property
    def vulnerabilities(self):
        return VulnerabilityPerson.objects.all(person=self).all()

    def create_identifier(self):
        try:
            p_lastest = Person.objects.filter(
                target__site_engistrement=self.target.site_engistrement
            ).latest("started_on")
            identifier = p_lastest.identifier[-4:]
        except Exception as e:
            print(e)
            identifier = "0000"
        return "S{s}{d}{id}".format(
            s=self.target.site_engistrement.slug,
            d="{}{}".format(self.target.date.split("-")[0],
                            self.target.date.split("-")[1]),
            id=self.add(identifier, "1"))

    def add(self, x, y):
        r = str(int(x) + int(y)).zfill(len(x))
        return r

    def get_qrcode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4)

        qr.add_data(self.identifier)
        qr.make(fit=True)
        im = qr.make_image()
        output = io.BytesIO()
        im.save(output, format="PNG")
        output.seek(0)
        return output

    def __str__(self):
        return self.name()

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self.create_identifier()
        self.is_invalide_num_pi = invalide_num_progres_individuel(
            self.num_progres_individuel)
        self.is_num_pi_sans_num_pm = self.num_pi_sans_num_pm()
        self.is_not_empty_num_pi_alg = self.not_empty_num_pi_alg()
        self.is_vrf_wihtout_num_pi = self.vrf_wihtout_num_pi()
        self.is_doublon_pm_pi = self.num_pi_existe()
        self.is_sans_doc_avec_num_pi = no_doc_with_num_pi(self.num_progres_individuel)

        super(Person, self).save(*args, **kwargs)

    @property
    def validated(self):
        return (self.is_invalide_num_pi or
                self.is_num_pi_sans_num_pm or
                self.is_not_empty_num_pi_alg or
                self.is_vrf_wihtout_num_pi or
                self.is_doublon_pm_pi or
                self.is_sans_doc_avec_num_pi)

    def num_pi_existe(self):
        from repatriate.models import Person
        if not self.num_progres_individuel:
            return False
        # duplicate_mg = False
        duplicate_pn = False
        d_pn = Person.active_objects.exclude(
            identifier=self.identifier).filter(
            num_progres_individuel=self.num_progres_individuel)
        if d_pn:
            duplicate_pn = True
            # if d_pn.target.num_progres_menage == self.target.num_progres_menage:
            #     duplicate_mg = True
        return duplicate_pn

    def num_pi_sans_num_pm(self):
        if self.target.num_progres_menage == "" and self.num_progres_individuel != "":
            return True
        return False

    def not_empty_num_pi_alg(self):
        if self.target.pays_asile == "algerie" and self.num_progres_individuel:
            return True
        return False

    def vrf_wihtout_num_pi(self):
        if self.target.chef_doc == "formulaire_de_retour_volontaire" and not self.num_progres_individuel:
            return True
        return False
