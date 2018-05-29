#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json
# import re
# import logging
import os
import reversion
from django.db import models
from django.conf import settings
from django.urls import reverse

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from collections import OrderedDict
from desk.models import Provider


class Country(models.Model):
    slug = models.SlugField(_("Slug"), max_length=75, primary_key=True)
    name = models.CharField(_("Name"), max_length=250)

    @classmethod
    def get_or_create(cls, slug, name):
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return cls.objects.create(slug=slug, name=name)

    def __str__(self):
        return self.name


class Survey(models.Model):

    NOT_APPLICABLE = 'not_applicable'
    # Integrity Status
    NOT_CHECKED = 'not_checked'
    INCORRECT = 'incorrect'
    CORRECT = 'correct'
    INTEGRITY_STATUSES = {
        NOT_CHECKED: _("Not Checked"),
        INCORRECT: _("Incorrect"),
        CORRECT: _("Correct")
    }

    # Validation
    NOT_VALIDATED = 'not_validated'
    VALIDATED = 'validated'
    REFUSED = 'refused'
    VALIDATION_STATUSES = {
        NOT_VALIDATED: _("Not Validated"),
        VALIDATED: _("Validated"),
        REFUSED: _("Refused"),
        NOT_APPLICABLE: _("N/a")
    }

    class Meta:
        ordering = ['date_entretien', 'date_arrivee', ]
        # unique_together = (('instance_id'),)

    # last Provider who edited report. Initialized with created_by
    modified_by = models.ForeignKey(Provider,
                                    null=True, blank=True,
                                    verbose_name=_("Modified By"),
                                    related_name='own_modified_reports')
    # last time report was edited. Initialized with created_on
    modified_on = models.DateTimeField(default=timezone.now,
                                       verbose_name=_("Modified On"))
    completed_on = models.DateTimeField(null=True, blank=True)
    # Integrity State: wheter data are correct or not (!= validation)
    integrity_status = models.CharField(max_length=40,
                                        choices=INTEGRITY_STATUSES.items(),
                                        default=NOT_CHECKED)
    # Validation State
    validation_status = models.CharField(max_length=40,
                                         choices=VALIDATION_STATUSES.items(),
                                         default=NOT_APPLICABLE)
    validated_on = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(Provider,
                                     null=True, blank=True,
                                     verbose_name=_("Validated By"),
                                     related_name='own_validated_reports')
    auto_validated = models.BooleanField(default=False)

    instance_id = models.CharField(
        _("Instance ID"), max_length=100, primary_key=True)
    formhub_uuid = models.CharField(max_length=250)
    submission_date = models.DateTimeField(
        _("Date de soumission"))
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    type_operation = models.CharField(_("Operation Type"), max_length=120)
    cause = models.CharField(_("Cause"), max_length=120, blank=True, null=True)
    cause_other = models.CharField(
        _("Cause"), max_length=120, blank=True, null=True)
    nom_agent = models.CharField(_("Agent"), max_length=120)
    date_arrivee = models.DateField()
    date_entretien = models.DateField()
    menage_point_entrer = models.CharField(
        verbose_name=_("Point entre"), max_length=100)
    menage_pays_provenance = models.ForeignKey(
        Country, verbose_name=_("Pays provenance"),
        related_name='pays_provenances', blank=True, null=True)
    menage_pays_de_provenance_ville = models.CharField(max_length=100)
    membre_pays_provenance = models.BooleanField(default=False)
    retour_rejoidre_famille = models.BooleanField(default=False)
    menage_doc_voyage = models.CharField(max_length=100)
    menage_numero_doc_voyage = models.CharField(max_length=250)
    faire_venir_famille = models.BooleanField(default=False)
    menage_photo_doc_voyage = models.CharField(max_length=100)
    menage_bien_pays_provenance = models.BooleanField(default=True, blank=True)
    nb_membre = models.IntegerField(
        verbose_name=_("Nombre de membre non embarqué"), default=0)
    # menage = models.ForeignKey(Menage, blank=True)
    adresse_mali_lieu_region = models.CharField(
        verbose_name=_("Region"), max_length=100, blank=True, null=True)
    # localite = models.ForeignKey(
    #     Entity, verbose_name=_("Localite"), related_name='Entities')
    adresse_mali_lieu_cercle = models.CharField(
        verbose_name=_("Cercle résidence"),
        max_length=100, blank=True, null=True)
    adresse_mali_lieu_commune = models.CharField(
        verbose_name=_("Commune résidence"),
        max_length=100, blank=True, null=True)
    adresse_mali_lieu_village_autre = models.CharField(
        verbose_name=_("Village résidence"),
        max_length=100, blank=True, null=True)
    rue = models.CharField(max_length=100, blank=True, null=True)
    porte = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=100, blank=True, null=True)
    bonne_sante = models.BooleanField(
        verbose_name=_("Bonne Santé"), default=True)
    hebergement = models.CharField(max_length=100, blank=True, null=True)
    hebergement_other = models.CharField(max_length=100, blank=True, null=True)
    maladie_chronique = models.CharField(max_length=100, blank=True, null=True)
    maladie_chronique_other = models.CharField(
        max_length=100, blank=True, null=True)
    prise_medicaments = models.CharField(max_length=100, blank=True, null=True)
    medicaments = models.CharField(max_length=100, blank=True, null=True)
    fromation_pro = models.BooleanField(
        verbose_name=_("Formation"), default=True)
    domaine = models.CharField(max_length=100, blank=True, null=True)
    formation_experience_secteur = models.CharField(
        max_length=80, blank=True, null=True)
    metier = models.BooleanField(
        verbose_name=_("Job"), default=True)
    reinsertion_professionnelle_f1 = models.BooleanField(
        default=True, verbose_name=_(
            "F1. Formation socio-professionnelle souhaitée ?"))
    reinsertion_professionnelle_f2 = models.CharField(
        blank=True, null=True, max_length=200, verbose_name=_(
            "F2. Dans quel secteur ?"))
    reinsertion_professionnelle_f3 = models.BooleanField(
        default=True, verbose_name=_("F3. Avez-vous un Projet d’activité ?"))
    reinsertion_professionnelle_f4 = models.CharField(
        blank=True, null=True, max_length=200, verbose_name=_(
            "F4. Lequel?"))
    reinsertion_professionnelle_f5 = models.CharField(
        blank=True, null=True, max_length=200, verbose_name=_(
            "F5. Que souhaiterez-vous faire ?"))
    reinsertion_professionnelle_f6_activite_region = models.CharField(
        max_length=100, blank=True, null=True)
    reinsertion_professionnelle_f6_activite_cercle = models.CharField(
        max_length=100, blank=True, null=True)
    reinsertion_professionnelle_f6_activite_commune = models.CharField(
        max_length=100, blank=True, null=True)
    reinsertion_professionnelle_f6_activite_village_autre = models.CharField(
        max_length=100, blank=True, null=True)
    observations = models.TextField(
        verbose_name=_("Observations"), max_length=100, blank=True, null=True)

    def __str__(self):
        return "{instance_id} - {nom_agent} - {lieu_region}".format(
            instance_id=self.instance_id, nom_agent=self.nom_agent,
            lieu_region=self.adresse_mali_lieu_region)

    def person_url(self):
        return reverse("person_table", args=[self.instance_id])

    def get_menage_photo_doc_voyage_name(self, name):
        return os.path.splitext(name)[0].split('-')[0]

    @property
    def get_menage_photo_doc_voyage(self):
        name, exten = os.path.splitext(os.path.basename(self.menage_photo_doc_voyage))
        return os.path.join(
            os.path.dirname(self.menage_photo_doc_voyage),
            name.split('-')[0] + exten)

    # @property
    # def get_menage_photo_doc_voyage_url(self):
    #     return os.path.join(
    #         settings.BASE_ODK_DIR, self.get_menage_photo_doc_voyage_name(
    #             self.menage_photo_doc_voyage))

    def persons(self):
        return Person.objects.filter(survey=self)

    @property
    def nb_member(self):
        return self.persons().count()


class Person(models.Model):

    class Meta:
        unique_together = (('key_odk'), ('identifier'))
        ordering = ['survey__date_entretien']

    CELI = 'celibataire'
    MARIE = 'marie'
    ETAT_CIVIL = OrderedDict([
        (CELI, "celibataire"),
        (MARIE, "Marie")
    ])
    MALE = 'male'
    FEMALE = 'female'
    GENDERS = OrderedDict([
        (MALE, "Masculin"),
        (FEMALE, "Feminin")
    ])
    SEXES = OrderedDict([
        (MALE, "Homme"),
        (FEMALE, "Femme")
    ])

    identifier = models.CharField(
        _("identifier"), max_length=80, null=True, blank=True)
    key_odk = models.CharField(max_length=100)
    date = models.DateTimeField(_("Date"), default=timezone.now)
    survey = models.ForeignKey(Survey)
    age = models.IntegerField(verbose_name=_("Age"))
    gender = models.CharField(max_length=20, choices=GENDERS.items())
    type_naissance = models.CharField(max_length=30)
    nationalite = models.CharField(
        verbose_name=_("Nationalite"), max_length=50, blank=True, null=True)
    prenoms = models.CharField(_("First name"), max_length=120)
    nom = models.CharField(_("Last name"), max_length=120)
    annee_naissance = models.IntegerField(
        verbose_name=_("Annee de naissance"), blank=True, null=True)
    ddn = models.DateField(
        verbose_name=_("Date de naissance"), blank=True, null=True)
    profession = models.CharField(
        verbose_name=_("Profession"), max_length=120, blank=True, null=True)
    profession_other = models.CharField(
        verbose_name=_("Profession"), max_length=120, blank=True, null=True)
    etat_civil = models.CharField(verbose_name=_("Etat Civil"),
                                  max_length=20, choices=ETAT_CIVIL.items())
    lien = models.CharField(verbose_name=_("Lien"), max_length=120)
    niveau_scolaire = models.CharField(max_length=100, blank=True)
    document = models.CharField(
        verbose_name=_("Document"), max_length=120, blank=True, null=True)
    num_doc = models.CharField(
        max_length=120, verbose_name=_("Numéro du document"),
        blank=True, null=True)
    nina = models.CharField(
        max_length=120, verbose_name=_("NINA"), blank=True, null=True)
    biometric = models.CharField(max_length=100, blank=True, null=True)
    saisie_nina = models.CharField(max_length=100, blank=True, null=True)
    saisie_biometric = models.CharField(max_length=100, blank=True, null=True)
    membre_vulnerabilite = models.BooleanField(default=False)
    membre_vul1 = models.CharField(max_length=100, blank=True, null=True)
    membre_vul2 = models.CharField(max_length=100, blank=True, null=True)
    membre_vul3 = models.CharField(max_length=100, blank=True, null=True)
    membre_photo = models.CharField(
        max_length=500, blank=True, null=True)
    # membre_photo = models.ImageField(
    #     upload_to='membre_photo/%Y/%m/%d/', blank=True, verbose_name=(
    #         "Photo document de voyage"))

    def person_detail_url(self):
        return reverse("person", args=[self.id])

    @property
    def get_membre_photo_name(self):
        name, exten = os.path.splitext(
            os.path.basename(self.membre_photo))
        return os.path.join(
            os.path.dirname(self.membre_photo),
            name.split('-')[0] + exten)

    @property
    def verbose_sex(self):
        return self.SEXES.get(self.gender)

    def display_name(self):
        return "{m} {nom} {prenoms}".format(
            m="M." if self.gender == self.MALE else "Mme",
            nom=self.nom, prenoms=self.prenoms, age=self.age)

    def __str__(self):
        return "{}-{}".format(self.identifier, self.display_name())

    def create_identifier(self):
        try:
            p_lastest = Person.objects.filter(
                survey__adresse_mali_lieu_cercle=self.survey.adresse_mali_lieu_cercle).latest(
                "date")
            identifier = p_lastest.identifier[-5:]
        except Exception:
            identifier = "00000"
        return "M{r}{c}{id}".format(
            r=self.get_slug_region(self.survey.adresse_mali_lieu_region),
            c=self.get_slug_cercle(self.survey.adresse_mali_lieu_cercle),
            id=self.add(identifier, "1"))

    def get_code(self):
        with open(settings.CODES) as data_f:
            m_data = json.loads(data_f.read())
        return m_data

    def get_slug_region(self, region):
        return str(self.get_code().get(region))

    def get_slug_cercle(self, cercle):
        return self.add("000", str(self.get_code().get(cercle)))

    def add(self, x, y):
        r = str(int(x) + int(y)).zfill(len(x))
        return r

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self.create_identifier()
        super(Person, self).save(*args, **kwargs)

reversion.register(Person)
reversion.register(Survey)
