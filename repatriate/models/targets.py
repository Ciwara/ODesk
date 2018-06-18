#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
import os
from collections import OrderedDict

from django.db import models
# from django.utils import timezone
from jsonfield.fields import JSONField

from desk.utils import get_attachment, PERSONAL_FILES

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from desk.models import Provider
from repatriate.models import RegistrationSite

from repatriate.target_checks import (
    invalide_num_progres_menage, requise_num_progres_menage, invalide_num_tel,
    not_empty_num_progres_menage_alg, no_doc_with_num_pm, num_pm_existe,
    site_not_existe)

logger = logging.getLogger(__name__)


class NotFixManager(models.Manager):
    def get_queryset(self):
        return super(NotFixManager, self).get_queryset().filter(fixed=False)


class DuplicateProgresMenage(models.Model):

    class Meta:
        unique_together = (('old_target', 'new_target'),)
        ordering = ['-detection_date']

    old_target = models.ForeignKey("Target", related_name='old_targets')
    new_target = models.ForeignKey("Target", related_name='new_targets')
    fixed_by = models.ForeignKey(
        Provider, related_name="fixed_by_provider", null=True, blank=True)
    detection_date = models.DateTimeField(
        "Date de detection", default=timezone.now)
    fix_date = models.DateTimeField("Date de correction", default=timezone.now)
    fixed = models.BooleanField("Corriger", default=False)

    objects = models.Manager()
    not_fix_objects = NotFixManager()

    def __str__(self):
        return "{old_target}/{new_target}/{fixed_by}".format(
            old_target=self.old_target, new_target=self.new_target,
            fixed_by=self.fixed_by)

    def merge_manager_url(self):
        return reverse('merge_manager', kwargs={'id': self.id})


class OrganizationTarget(models.Model):

    class Meta:
        unique_together = (('organization', 'target'),)

    organization = models.CharField(blank=True, null=True, max_length=100)
    target = models.ForeignKey(
        "Target", related_name='organization_target_targets')

    def __str__(self):
        return "{organization}.{target}".format(
            organization=self.organization, target=self.target)


class TargetTypeAssistance(models.Model):

    class Meta:

        unique_together = (('type_assistance', 'target'),)

    type_assistance = models.CharField(blank=True, null=True, max_length=100)
    target = models.ForeignKey(
        "Target", related_name='type_assistance_targets')

    def __str__(self):
        return "{type_assistance} - {target}".format(
            type_assistance=self.type_assistance, target=self.target)


class TargetManager(models.Manager):
    def get_queryset(self):
        return super(TargetManager, self).get_queryset().filter(deleted=False)


class TargetValidateManager(models.Manager):
    def get_queryset(self):
        return super(TargetValidateManager, self).get_queryset().filter(
            deleted=False, is_validated=True)


class Target(models.Model):

    # Completion Status
    COMPLETE = 'complete'
    INCOMPLETE = 'incomplete'
    COMPLETION_STATUSES = {
        COMPLETE: _("Complete"),
        INCOMPLETE: _("Incomplete")
    }

    NOT_APPLICABLE = 'not_applicable'
    # Integrity Status
    NOT_CHECKED = 'not_checked'
    INCORRECT = 'incorrect'
    CORRECT = 'correct'

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

    AI = "activite-indiv"
    AG = "activite-groupe"
    IEDE = "integre-entreprise"
    NSP = "ne_sait_pas"

    ACTIVITES_TYPES = OrderedDict([
        (AI, "Mettre en place  une activité individuelle"),
        (AG, "Mettre en place  une activité de groupe"),
        (IEDE, "Intégrer une entreprise déjà existante"),
        (NSP, "Ne sait pas")
    ])
    P = "proprietaire"
    L = "location"
    F = "famille"
    FA = "famille-accueil"

    HEBERGEMENTS = OrderedDict([
        (P, "Proprietaire"),
        (L, "Location"),
        (F, "Famille"),
        (FA, "Famille d'accueil")
    ])
    MA = "MA"
    CE = "CE"
    VV = "VV"
    SR = "SR"
    DV = "DV"
    FC = "FC"
    ETAT_CIVIL = OrderedDict([
        (MA, "Marié, mariée"),
        (CE, "Celibataire"),
        (VV, "Veuve, veuf"),
        (SR, "Separé, separée"),
        (DV, "Divorcé, divorcée"),
        (FC, "Fiancé, fiancée"),
    ])
    AB = "abris"
    VI = "viatique"
    AL = "alimentaire"
    ED = "education"
    NO = "nourriture"
    PR = "protection"
    ASSISTANCES = OrderedDict([
        (AB, "Abris"),
        (VI, "Viatique"),
        (AL, "Alimentaire"),
        (ED, "Éducation"),
        (NO, "Nourriture"),
        (PR, "Protection"),
    ])
    Ag = "agriculture"
    EL = "elevage"
    PC = "petit-commerce"
    SECTEURS = OrderedDict([
        (Ag, "Agriculture"),
        (EL, "Elevage"),
        (PC, "Petit commerce")
    ])
    FR = "formulaire_de_retour"
    AR = "attestation_de_refugie"
    CR = "carte_des_ration"
    SD = "sdoc"
    DOC_ENREGISTREMENT = OrderedDict([
        (FR, "Formulaire de retour volontaire"),
        (AR, "Attestation de réfugié"),
        (CR, "Carte des ration"),
        (SD, "Sans document")
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
        ordering = ['-collect__started_on', 'identifier']

    # last time report was edited. Initialized with created_on
    modified_on = models.DateTimeField(default=timezone.now,
                                       verbose_name=_("Modified On"))
    # last Provider who edited report. Initialized with created_by
    modified_by = models.ForeignKey(Provider,
                                    null=True, blank=True,
                                    verbose_name=_("Modified By"),
                                    related_name='repat_own_modified_reports')
    # Validation State
    validation_status = models.CharField(max_length=40,
                                         choices=VALIDATION_STATUSES.items(),
                                         default=NOT_APPLICABLE)
    validated_on = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(
        Provider, null=True, blank=True, verbose_name=_("Validated By"),
        related_name='repat_own_validated_reports')
    duration = models.IntegerField(default=0)
    submission_time = models.DateTimeField("Date de soumission", null=True, blank=True)
    identifier = models.CharField(max_length=100, primary_key=True)
    collect = models.ForeignKey('Collect', related_name='targets')
    instance_id = models.CharField(max_length=100)
    form_dataset = JSONField(default=dict, blank=True)
    # objects = models.Manager()
    date = models.DateField()
    debut = models.DateTimeField(default=timezone.now)
    fin = models.DateTimeField(default=timezone.now)
    nom_agent = models.CharField("Nom de l'agent", blank=True, max_length=100)
    num_enregistrement = models.CharField(
        "Numéro d'enregistrement", blank=True, max_length=100)
    site_engistrement = models.ForeignKey(
        RegistrationSite, verbose_name="Site d'enregestrement",
        related_name="target_registration_sites")
    date_arrivee = models.DateField("Date d'arrivée", blank=True, max_length=100)
    date_entretien = models.DateField(blank=True, max_length=100)
    continent_asile = models.CharField(blank=True, null=True, max_length=100)
    pays_asile = models.CharField(blank=True, null=True, max_length=100)
    ville_asile = models.CharField(blank=True, null=True, max_length=100)
    camp = models.CharField(blank=True, null=True, max_length=100)
    camp_other = models.CharField(blank=True, null=True, max_length=100)
    # num_progres_menage_alg = models.CharField(null=True, blank=True, max_length=100)
    num_progres_menage = models.CharField("Numéro progres", null=True, blank=True, max_length=50)
    point_de_entree = models.CharField("Point d'entrée", null=True, blank=True, max_length=100)
    continent_naissance = models.CharField(null=True, blank=True, max_length=100)
    pays_naissance = models.CharField(null=True, blank=True, max_length=100)
    lieu_naissance = models.CharField(null=True, blank=True, max_length=100)
    chef_etat_civil = models.CharField(
        max_length=20, choices=ETAT_CIVIL.items())
    chef_profession = models.CharField(blank=True, null=True, max_length=100)
    chef_doc = models.CharField(
        null=True, blank=True, max_length=100, choices=DOC_ENREGISTREMENT.items())
    num_doc = models.CharField(blank=True, null=True, max_length=100)
    beneficiez_lassistance = models.BooleanField(default=False)
    type_assistance_other = models.CharField(blank=True, null=True, max_length=50)
    organisations_other = models.CharField(blank=True, null=True, max_length=50)
    actuelle_region = models.CharField(blank=True, max_length=100)
    actuelle_cercle = models.CharField(blank=True, max_length=100)
    actuelle_commune = models.CharField(blank=True, max_length=100)
    actuelle_qvf = models.CharField(null=True, blank=True, max_length=100)
    actuelle_nom_generale_utilise = models.CharField(null=True, blank=True, max_length=100)
    rue = models.CharField(null=True, blank=True, max_length=100)
    porte = models.CharField(null=True, blank=True, max_length=100)
    tel = models.CharField("Numéro de Téléphone", null=True, blank=True, default=0, max_length=20)
    tel2 = models.CharField("Numéro de Téléphone2", null=True, blank=True, default=0, max_length=20)
    abris = models.BooleanField(default=False)
    nature_construction = models.CharField(null=True, blank=True, max_length=100)
    nature_construction_other = models.CharField(
        null=True, blank=True, max_length=100)
    type_hebergement = models.CharField(
        max_length=20, blank=True, null=True, choices=HEBERGEMENTS.items())
    type_hebergement_other = models.CharField(
        null=True, blank=True, max_length=100)
    nb_membre = models.IntegerField(null=True, blank=True, default=0)
    membre_pays = models.BooleanField(default=True)
    nbre_membre_reste = models.IntegerField(null=True, blank=True, default=0)
    # Sante_Appuipyschosocial
    etat_sante = models.BooleanField(default=True)
    situation_maladie = models.CharField(null=True, blank=True, max_length=100)
    type_maladie = models.CharField(null=True, blank=True, max_length=100)
    type_maladie_other = models.CharField(
        null=True, blank=True, max_length=100)
    type_aigue = models.CharField(null=True, blank=True, max_length=100)
    type_aigue_other = models.CharField(
        null=True, blank=True, max_length=100)
    prise_medicament = models.CharField(null=True, blank=True, max_length=100)
    type_medicaments = models.CharField(null=True, blank=True, max_length=100)
    # formation_experience
    suivi_formation = models.BooleanField(default=False)
    domaine_formation = models.CharField(null=True, blank=True, max_length=100)
    metier_pays_prove = models.BooleanField(default=False)
    exercice_secteur = models.CharField(
        null=True, blank=True, max_length=100, choices=SECTEURS.items())
    exercice_secteur_other = models.CharField(
        null=True, blank=True, max_length=100)
    # reinsertion_prof
    formation_socio_prof = models.BooleanField(default=False)
    secteur_prof = models.CharField(null=True, blank=True, max_length=100)
    secteur_prof_other = models.CharField(null=True, blank=True, max_length=100)
    projet_activite = models.BooleanField(default=False)
    type_projet = models.CharField(null=True, blank=True, max_length=100)
    souhait_activite = models.CharField(
        null=True, max_length=20, blank=True, choices=ACTIVITES_TYPES.items())
    souhait_activite_other = models.CharField(
        null=True, blank=True, max_length=100)
    # lieu_activite
    lieu_region = models.CharField(null=True, blank=True, max_length=100)
    lieu_cercle = models.CharField(null=True, blank=True, max_length=100)
    lieu_commune = models.CharField(null=True, blank=True, max_length=100)
    lieu_qvf = models.CharField(null=True, blank=True, max_length=100)
    lieu_non_generale_utilise = models.CharField(null=True, blank=True, max_length=100)
    signature = models.CharField(blank=True, max_length=200)
    deleted = models.BooleanField(default=False)

    # Checks
    is_requise_num_progres_menage = models.BooleanField(default=True)
    is_invalide_num_progres_menage = models.BooleanField(default=True)
    is_not_empty_num_progres_menage_alg = models.BooleanField(default=True)
    is_invalide_num_tel = models.BooleanField(default=True)
    is_no_doc_with_num_pm = models.BooleanField(default=True)
    is_site_not_existe = models.BooleanField(default=True)
    # is_num_pm_existe = models.BooleanField(default=True)
    is_validated = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = TargetManager()
    validate_objects = TargetValidateManager()

    @property
    def validated(self):
        return (self.is_requise_num_progres_menage or
                self.is_invalide_num_progres_menage or
                self.is_not_empty_num_progres_menage_alg or
                self.is_invalide_num_tel or
                self.is_no_doc_with_num_pm or
                self.is_site_not_existe)

    # def merge_manager_url(self):
    #     return reverse('merge_manager', kwargs={'id': self.identifier})

    def get_absolute_url(self):
        return reverse('correction_target', kwargs={'id': self.identifier})

    def end_merge_url(self):
        return reverse('end_merge_target', kwargs={'id': self.identifier})

    @property
    def type_assistance(self):
        return TargetTypeAssistance.objects.filter(target=self).all()

    @property
    def organisations(self):
        return OrganizationTarget.objects.filter(target=self).all()

    def name(self):
        # return self.num_progres_menage
        return "{site} - {num_p_m}".format(
            site=self.tel,
            num_p_m=self.num_progres_menage)

    @property
    def dataset(self):
        dataset = self.form_dataset.copy()
        for key, value in self.scan_form_dataset.items():
            if key not in dataset:
                dataset.update({key: value})
            elif key == '_attachments':
                dataset[key] += value
            else:
                dataset.update({"_scan:{}".format(key): value})
        return dataset

    def __str__(self):
        return "{ident}.{name}".format(ident=self.identifier, name=self.name())

    @classmethod
    def get_or_none(cls, identifier):
        try:
            return cls.objects.get(identifier=identifier)
        except cls.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self.instance_id

        self.is_requise_num_progres_menage = requise_num_progres_menage(
            self.pays_asile, self.num_progres_menage)
        self.is_invalide_num_progres_menage = invalide_num_progres_menage(
            self.num_progres_menage)
        self.is_invalide_num_tel = invalide_num_tel(self.tel)
        self.is_not_empty_num_progres_menage_alg = not_empty_num_progres_menage_alg(
            self.pays_asile, self.num_progres_menage)
        self.is_no_doc_with_num_pm = no_doc_with_num_pm(
            self.chef_doc, self.num_progres_menage)
        self.is_site_not_existe = site_not_existe(self.site_engistrement)
        num_pm_existe(self)
        super(Target, self).save(*args, **kwargs)

    def delete(self):
        self.deleted = True
        self.save()

    def restory(self):
        self.deleted = False
        self.save()

    def attachments(self):

        labels = {
            'acte-naissance/image_acte_naissance': {
                'slug': 'acte_naissance',
                'short': "AN",
                'long': "Acte de naissance",
            },
            'carte-identite/image_carte_identite': {
                'slug': 'carte-identite',
                'short': "CI",
                'long': "Carte d'identité",
            },
            'signature': {
                'slug': 'signature',
                'short': "SIG",
                'long': "Signature",
            },
            'certificat-indigence': {
                'slug': 'certificat-indigence',
                'short': "CERT-IND",
                'long': "Certificat d'indigence",
            },
            'certificat-residence': {
                'slug': 'certificat-residence',
                'short': "CERT-RES",
                'long': "Certificat de résidence",
            },
        }

        spouses_labels = {
            'epouses/e_acte-mariage/e_image_m': {
                'slug': 'acte-mariage',
                'short': "AM",
                'long': "Acte de mariage",
            },
            'epouses/e_acte-naissance/e_image_n': {
                'slug': 'acte-naissance',
                'short': "AN",
                'long': "Acte de naissance",
            },
        }

        data = {
            'enfants': [],
            'epouses': []
        }

        # retrieve each expected image, add label and export fname
        for key, label in labels.items():
            attachment = get_attachment(self.dataset, self.dataset.get(key))
            if attachment is None:
                continue
            attachment['labels'] = label
            attachment['hamed_url'] = label['slug']
            attachment['export_fname'] = "{id}_{label}{ext}".format(
                id=self.identifier, label=label['slug'],
                ext=os.path.splitext(attachment['filename'])[1])
            data.update({label['slug']: attachment})
            del(attachment)

        # loop on spouses to apply same process
        for index, spouse in enumerate(self.dataset.get('epouses', [])):
            spouse_data = {}
            for key, label in spouses_labels.items():
                attachment = get_attachment(self.dataset, spouse.get(key))
                if attachment is None:
                    continue
                attachment['labels'] = label
                attachment['export_fname'] = \
                    "{id}_epouse{num}_{label}{ext}".format(
                    id=self.identifier,
                    num=index + 1,
                    label=label['slug'],
                    ext=os.path.splitext(attachment['filename'])[1])
                spouse_data.update({label['slug']: attachment})
                del(attachment)
            data['epouses'].append(spouse_data)

        return data

    def get_attachment(self, slug, within=None, at_index=None):
        ''' retrieve single (or several) attachment for specific slug

            within: enfants | epouses
            at_index: specify 0-based entry within the `within` group '''

        # root-level (enquetee) attachment
        if within is None:
            return self.attachments().get(slug)

        # attachments for that slug for each of the group members
        if at_index is None:
            return [att.get(slug)
                    for att in self.attachments().get(within, [])]

        try:
            return self.attachments().get(within)[at_index].get(slug)
        except IndexError:
            return None

    def list_attachments(self):
        al = []
        for attach_key, attachment in self.attachments().items():
            if attach_key == 'signature':
                continue
            if isinstance(attachment, list):
                for person in attachment:
                    for pattach_key, pattachment in person.items():
                        al.append(pattachment)
            else:
                al.append(attachment)
        return al

    def get_folder_fname(self):
        return self.fname()

    def get_folder_path(self):
        return os.path.join(self.collect.get_documents_path(),
                            PERSONAL_FILES,
                            self.get_folder_fname())

    def export_data(self):
        data = self.dataset.copy()
        data.update({'_hamed_attachments': self.attachments()})
        return data

    @property
    def ona_submission_id(self):
        return self.form_dataset.get('_id')

    def get_membres(self):
        from repatriate.models import Person
        return Person.objects.filter(target=self, deleted=False)

    # Check functions

    def zero_member(self):
        return self.get_membres().count() == 0

    def many_chef_menage(self):
        from repatriate.models import Person
        if Person.objects.filter(target=self, membre_lien="chef_de_famille").count() != 1:
            return True
        return False

    def no_chef_manage(self):
        from repatriate.models import Person
        if Person.objects.filter(
                target=self, membre_lien="chef_de_famille").count() == 0:
            return True
        return False

    def same_num_pm(self):
        return Target.objects.filter(
            deleted=False, num_progres_menage=self.num_progres_menage)

    # def num_pm_existe(self):
    #     return self.same_num_pm().count() > 0


# models.signals.post_save.connect(checker, sender=Target)
