#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json
import re
from django.db import models

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
from django.core import validators
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from collections import OrderedDict


_s = lambda l: sorted(l, key=lambda e: e.name)


class MemberManager(BaseUserManager):
    def create_user(self, email, username, date_of_birth=None,
                    password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError('Users must have an username')
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            # date_of_birth=date_of_birth,
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password,
                         email=None, date_of_birth=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            # date_of_birth=date_of_birth,
            username=username,
        )
        user.is_admin = True
        user.is_active = True
        # user.has_perm = True
        user.save(using=self._db)
        return user


class Member(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    username = models.CharField(
        _("username"), max_length=50, primary_key=True,
        help_text=_("Required. 50 characters or fewer. "
                    "Letters, numbers and @/./+/-/_ characters"),
        validators=[validators.RegexValidator(re.compile("^[\w.@+-]+$"),
                                              _("Enter a valid username."),
                                              "invalid")])

    first_name = models.CharField(max_length=100, blank=True, null=True,
                                  verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, blank=True, null=True,
                                 verbose_name=_("Last Name"))
    image = models.ImageField(upload_to='images_member/', blank=True,
                              verbose_name=_("Photo"))
    email = models.EmailField(_("email address"), blank=True, null=True)
    is_staff = models.BooleanField(_("staff status"), default=False,
                                   help_text=_(
        "Designates whether the user can log into this admin site."))
    is_active = models.BooleanField(
        _("active"), default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."))
    date_of_birth = models.DateField(
        blank=True, null=True, default=timezone.now)
    is_admin = models.BooleanField(default=False)
    objects = MemberManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name()

    def get_short_name(self):
        return self.name()

    def name(self):
        if not self.first_name and not self.last_name:
            return self.username
        elif not self.first_name:
            return self.last_name
        else:
            return self.first_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class EntityQuerySet(models.QuerySet):

    def active(self):
        return self.filter(active=True)


class EntityType(models.Model):

    class Meta:
        app_label = 'desk'
        verbose_name = _("Entity Type")
        verbose_name_plural = _("Entity Types")

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(_("Name"), max_length=30)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_none(cls, slug):
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None


class Entity(MPTTModel):

    class Meta:
        app_label = 'desk'
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(_("Name"), max_length=50)
    type = models.ForeignKey(EntityType, related_name='entities',
                             verbose_name=_("Type"))
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            verbose_name=_("Parent"))
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(default=timezone.now)

    objects = TreeManager()

    def __str__(self):
        return self.name

    @property
    def geojson(self):
        return json.loads(self.geometry)

    def to_dict(self):
        return {'slug': self.slug,
                'name': self.name,
                'type': self.type.slug,
                'parent': getattr(self.parent, 'slug', None),
                'latitude': self.latitude,
                'longitude': self.longitude}

    def display_name(self):
        return self.name.title()

    def display_full_name(self):
        if self.parent:
            return ugettext("{name}/{parent}").format(
                name=self.display_name(),
                parent=self.parent.display_name())
        return self.display_name()

    def display_code_name(self):
        return ugettext("{code}/{name}").format(
            code=self.slug, name=self.display_name())

    def parent_level(self):
        if self.parent:
            return self.parent.type
        # return self.parent
        return "NO PARENT"

    @property
    def gps(self):
        if self.latitude is not None and self.longitude is not None:
            return "{lat},{lon}".format(lat=self.latitude, lon=self.longitude)


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

    class Meta:
        ordering = ['date_arrivee', ]

    instanceID = models.SlugField(
        _("Instance ID"), max_length=250, primary_key=True)
    uuid = models.CharField(_("Slug"), max_length=250)
    name_form = models.CharField(_("Name"), max_length=250)
    region = models.CharField(max_length=100)
    cercle = models.CharField(max_length=100)
    commune = models.CharField(max_length=100)
    village = models.CharField(max_length=100)

    debut = models.DateTimeField(_("Start"), default=timezone.now)
    fin = models.DateTimeField(_("End"), default=timezone.now)
    type_operation = models.CharField(_("Operation Type"), max_length=120)
    cause = models.CharField(_("Cause"), max_length=120, blank=True, null=True)
    nom_agent = models.CharField(_("Agent"), max_length=120)
    date_arrivee = models.DateField()
    date_ebtretien = models.DateField()
    menage_point_entrer = models.CharField(verbose_name=_("Point entre"), max_length=100)
    menage_ville = models.CharField(verbose_name=_("Point entre"), max_length=100)
    menage_pays_provenance = models.ForeignKey(
        Country, verbose_name=_("Pays provenance"), related_name='pays_provenances', blank=True, null=True)
    membre_pays_provenance = models.BooleanField(default=False)
    menage_doc_voyage = models.CharField(max_length=100)
    menage_numero_doc_voyage = models.CharField(max_length=250)
    menage_photo_doc_voyage_url_odk = models.CharField(max_length=250)
    menage_photo_doc_voyage = models.ImageField(
        upload_to='menage_photo_doc_voyage/%Y/%m/%d/', blank=True, verbose_name=(
            "Photo document de voyage"))
    menage_bien_pays_provenance = models.BooleanField(default=True, blank=True)
    nb_membre = models.IntegerField(
        verbose_name=_("Nombre de membre non embarqué"), default=0)
    # menage = models.ForeignKey(Menage, blank=True)
    lieu_region = models.CharField(verbose_name=_("Region"), max_length=100, blank=True, null=True)
    # localite = models.ForeignKey(
    #     Entity, verbose_name=_("Localite"), related_name='Entities')
    lieu_cercle = models.CharField(
        verbose_name=_("Cercle résidence"), max_length=100, blank=True, null=True)
    lieu_commune = models.CharField(
        verbose_name=_("Commune résidence"), max_length=100, blank=True, null=True)
    lieu_village_autre = models.CharField(
        verbose_name=_("Village résidence"), max_length=100, blank=True, null=True)
    rue = models.CharField(max_length=100, blank=True, null=True)
    porte = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=100, blank=True, null=True)
    bonne_sante = models.BooleanField(
        verbose_name=_("Bonne Santé"), default=True)
    hebergement = models.CharField(max_length=100, blank=True, null=True)
    maladie_chronique = models.CharField(max_length=100, blank=True, null=True)
    prise_medicaments = models.CharField(max_length=100, blank=True, null=True)
    medicaments = models.CharField(max_length=100, blank=True, null=True)
    fromation_pro = models.BooleanField(
        verbose_name=_("Formation"), default=True)
    domaine = models.CharField(max_length=100, blank=True, null=True)
    metier = models.BooleanField(
        verbose_name=_("Job"), default=True)
    f1 = models.BooleanField(default=True, verbose_name=_(
        "F1. Formation socio-professionnelle souhaitée ?"))
    f2 = models.CharField(null=True, max_length=200, verbose_name=_(
        "F2. Dans quel secteur ?"))
    f3 = models.BooleanField(default=True, verbose_name=_(
        "F3. Avez-vous un Projet d’activité ?"))
    f4 = models.CharField(null=True, max_length=200, verbose_name=_(
        "F4. Lequel?"))
    f5 = models.CharField(null=True, max_length=200, verbose_name=_(
        "F5. Que souhaiterez-vous faire ?"))
    activite_region = models.CharField(max_length=100, blank=True, null=True)
    activite_cercle = models.CharField(max_length=100, blank=True, null=True)
    activite_commune = models.CharField(max_length=100, blank=True, null=True)
    activite_village_autre = models.CharField(
        max_length=100, blank=True, null=True),
    observations = models.CharField(
        verbose_name=_("Observations"), max_length=100, blank=True, null=True)

    def __str__(self):
        return "{instanceID} - {nom_agent} - {lieu_region}".format(
            instanceID=self.instanceID, nom_agent=self.nom_agent,
            lieu_region=self.lieu_region)

    def persons(self):
        return Person.objects.filter(survey=self)

    @property
    def nb_member(self):
        return self.persons().count()


class Person(models.Model):

    class Meta:
        unique_together = (('survey', 'prenoms', 'age', 'gender'),)

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

    survey = models.ForeignKey(Survey)
    age = models.IntegerField(verbose_name=_("Age"))
    gender = models.CharField(max_length=20, choices=GENDERS.items())
    nationalite = models.CharField(
        verbose_name=_("Nationalite"), max_length=120, blank=True, null=True)
    prenoms = models.CharField(_("First name"), max_length=120)
    nom = models.CharField(_("Last name"), max_length=120)
    annee_naissance = models.IntegerField(
        verbose_name=_("Annee de naissance"), blank=True, null=True)
    ddn = models.DateField(
        verbose_name=_("Date de naissance"), blank=True, null=True)
    profession = models.CharField(
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
    vulnerabilite = models.BooleanField(default=False)
    vul1 = models.CharField(max_length=100, blank=True, null=True)
    vul2 = models.CharField(max_length=100, blank=True, null=True)
    vul3 = models.CharField(max_length=100, blank=True, null=True)
    membre_photo_url_odk = models.CharField(
        max_length=100, blank=True, null=True)
    membre_photo = models.ImageField(
        upload_to='membre_photo/%Y/%m/%d/', blank=True, verbose_name=(
            "Photo document de voyage"))

    @property
    def verbose_sex(self):
        return self.SEXES.get(self.gender)

    def display_name(self):
        return "{m} {nom} {prenoms}".format(
            m="M." if self.gender == self.MALE else "Mme",
            nom=self.nom, prenoms=self.prenoms, age=self.age)

    def __str__(self):
        return "{nom} {prenoms} {age}".format(
            nom=self.nom, prenoms=self.prenoms, age=self.age)
