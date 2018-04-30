#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
import os
from collections import OrderedDict
import io
import qrcode

from django.db import models
# from django.utils import timezone
from jsonfield.fields import JSONField

# from hamed.identifiers import full_random_id
from desk.utils import get_attachment, PERSONAL_FILES
# from hamed.ona import delete_submission

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from desk.models import Entity, Provider, RegistrationSite

logger = logging.getLogger(__name__)


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
        return "{type_assistance}.{target}".format(
            type_assistance=self.type_assistance, target=self.target)


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
        ordering = ['-collect__started_on', 'chef_nom', 'chef_prenom']

    MALE = 'masculin'
    FEMALE = 'female'
    GENDERS = OrderedDict([
        (MALE, "Masculin"),
        (FEMALE, "Feminin")
    ])
    SEXES = OrderedDict([
        (MALE, "Homme"),
        (FEMALE, "Femme")
    ])

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
    F = "formulaire_de_retour"
    A = "attestation_de_refugie"
    C = "carte_des_ration"
    DOC_ENREGISTREMENT = OrderedDict([
        (F, "volontaire Formulaire de retour volontaire"),
        (A, "Attestation de réfugié"),
        (C, "Carte des ration")
    ])

    # last time report was edited. Initialized with created_on
    modified_on = models.DateTimeField(default=timezone.now,
                                       verbose_name=_("Modified On"))
    # last Provider who edited report. Initialized with created_by
    modified_by = models.ForeignKey(Provider,
                                    null=True, blank=True,
                                    verbose_name=_("Modified By"),
                                    related_name='repat_own_modified_reports')
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
                                     related_name='repat_own_validated_reports')

    identifier = models.CharField(max_length=100, primary_key=True)
    collect = models.ForeignKey('Collect', related_name='targets')
    instance_id = models.CharField(max_length=100)
    form_dataset = JSONField(default=dict, blank=True)
    # objects = models.Manager()
    date = models.DateField()
    debut = models.DateTimeField(default=timezone.now)
    fin = models.DateTimeField(default=timezone.now)
    nom_agent = models.CharField(blank=True, max_length=100)
    nu_enregistrement = models.CharField(blank=True, max_length=100)
    site_engistrement = models.ForeignKey(
        RegistrationSite, related_name="target_registrations_sites")
    date_arrivee = models.CharField(blank=True, max_length=100)
    date_entretien = models.CharField(blank=True, max_length=100)
    continent_asile = models.CharField(blank=True, max_length=100)
    pays_asile = models.CharField(blank=True, max_length=100)
    ville_asile = models.CharField(blank=True, max_length=100)
    camp = models.CharField(blank=True, null=True, max_length=100)
    num_progres_menage_alg = models.CharField(blank=True, max_length=100)
    num_progres_menage = models.CharField(blank=True, max_length=100)
    chef_nom = models.CharField(blank=True, max_length=100)
    chef_prenom = models.CharField(blank=True, max_length=100)
    chef_sexe = models.CharField(
        blank=True, max_length=20, choices=GENDERS.items())
    chef_etat_civil = models.CharField(
        max_length=20, choices=ETAT_CIVIL.items())
    chef_ddn = models.DateField(blank=True, max_length=100)
    chef_age = models.IntegerField(verbose_name=_("L'âge du chef de menage"))
    beneficiez_lassistance = models.BooleanField(default=False)
    continent_naissance = models.CharField(blank=True, max_length=100)
    pays_naissance = models.CharField(blank=True, max_length=100)
    lieu_naissance = models.CharField(blank=True, max_length=100)
    # chef_nom_pere = models.CharField(null=True, blank=True, max_length=100)
    # chef_nom_mere = models.CharField(null=True, blank=True, max_length=100)
    chef_profession = models.CharField(blank=True, null=True, max_length=100)
    point_de_entree = models.CharField(null=True, blank=True, max_length=100)
    chef_doc = models.CharField(
        null=True, blank=True, max_length=100, choices=DOC_ENREGISTREMENT.items())
    nu_doc = models.CharField(blank=True, max_length=100)
    # adresse_mali
    actuelle_region = models.CharField(blank=True, max_length=100)
    actuelle_cercle = models.CharField(blank=True, max_length=100)
    actuelle_commune = models.CharField(blank=True, max_length=100)
    actuelle_qvf = models.CharField(null=True, blank=True, max_length=100)
    actuelle_nom_generale_utilise = models.CharField(null=True, blank=True, max_length=100)
    rue = models.CharField(null=True, blank=True, max_length=100)
    porte = models.CharField(null=True, blank=True, max_length=100)
    tel = models.IntegerField(default=0)
    abris = models.BooleanField(default=False)
    nature_construction = models.CharField(blank=True, max_length=100)
    type_hebergement = models.CharField(
        max_length=20, blank=True, choices=HEBERGEMENTS.items())
    # Sante_Appuipyschosocial
    etat_sante = models.BooleanField(default=True)
    situation_maladie = models.CharField(blank=True, max_length=100)
    type_maladie = models.CharField(blank=True, max_length=100)
    type_aigue = models.CharField(blank=True, max_length=100)
    prise_medicament = models.CharField(blank=True, max_length=100)
    type_medicaments = models.CharField(blank=True, max_length=100)
    # formation_experience
    suivi_formation = models.BooleanField(default=False)
    domaine_formation = models.CharField(blank=True, max_length=100)
    metier_pays_prove = models.CharField(blank=True, max_length=100)
    exercice_secteur = models.CharField(
        null=True, blank=True, max_length=100, choices=SECTEURS.items())
    # reinsertion_prof
    formation_socio_prof = models.BooleanField(default=False)
    secteur_prof = models.CharField(null=True, blank=True, max_length=100)
    projet_activite = models.BooleanField(default=False)
    type_projet = models.CharField(null=True, blank=True, max_length=100)
    souhait_activite = models.CharField(
        null=True, max_length=20, blank=True, choices=ACTIVITES_TYPES.items())
    # lieu_activite
    lieu_region = models.CharField(null=True, blank=True, max_length=100)
    lieu_cercle = models.CharField(null=True, blank=True, max_length=100)
    lieu_commune = models.CharField(null=True, blank=True, max_length=100)
    lieu_qvf = models.CharField(null=True, blank=True, max_length=100)
    signature = models.CharField(blank=True, max_length=200)
    membre_pays = models.BooleanField(default=True)
    nbre_membre_reste = models.IntegerField(default=0)

    def type_assistance(self):
        return TargetTypeAssistance.objects.filter(target=self).all()

    def name(self):
        return "{first} {last}".format(
            last=self.chef_nom.upper(), first=self.chef_prenom.title())

    @property
    def verbose_sex(self):
        return self.SEXES.get(self.gender)

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

        children_labels = {
            'enfants/situation/enfant_certificat-frequentation/enfant_image_f':
            {
                'slug': 'certificat-frequentation',
                'short': "CERT-FREQ",
                'long': "Certificat de fréquentation",
            },
            'enfants/situation/enfant_certificat-medical/enfant_image_m': {
                'slug': 'certificat-medical',
                'short': "CERT-MED",
                'long': "Certificat médical",
            },
            'enfants/enfant_acte-naissance/enfant_image_n': {
                'slug': 'acte-naissance',
                'short': "AN",
                'long': "Acte de naissance",
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

        # loop on children to apply same process
        for index, children in enumerate(self.dataset.get('enfants', [])):
            children_data = {}
            for key, label in children_labels.items():
                attachment = get_attachment(self.dataset, children.get(key))
                if attachment is None:
                    continue
                attachment['labels'] = label
                attachment['export_fname'] = \
                    "{id}_enfant{num}_{label}{ext}".format(
                    id=self.identifier,
                    num=index + 1,
                    label=label['slug'],
                    ext=os.path.splitext(attachment['filename'])[1])
                children_data.update({label['slug']: attachment})
                del(attachment)
            data['enfants'].append(children_data)

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
