#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import re

import reversion
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, UserManager,
                                        PermissionsMixin)
from django.utils.translation import ugettext_lazy as _, ugettext
# from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.mail import send_mail
from django.core import validators
from django.utils import timezone
from django.core.urlresolvers import reverse
from mptt.models import TreeForeignKey
# from desk.signals import logged_in, logged_out
from desk.models.common import ActiveManager
from desk.models.Entities import Entity

from rolepermissions.roles import get_user_roles


class Project(models.Model):

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(max_length=200)
    desciption = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "{name}".format(name=self.name)


class EntityProvider(models.Model):

    class Meta:
        app_label = 'desk'
        verbose_name = _("EntityProvider")
        unique_together = (('locality', 'provider'),)

    locality = TreeForeignKey(Entity, related_name='entities',)
    provider = models.ForeignKey("Provider",)


class ProviderManager(UserManager):

    def create_superuser(self, username, email, password, **extra_fields):
        u = self.create_user(
            username=username, password=password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class Provider(AbstractBaseUser, PermissionsMixin):

    MALE = 'male'
    FEMALE = 'female'
    UNKNOWN = 'unknown'
    GENDERS = {
        MALE: _("Man"),
        FEMALE: _("Woman"),
        UNKNOWN: _("Unknown")
    }

    MISTER = 'mister'
    MISTRESS = 'mistress'
    MISS = 'miss'
    DOCTOR = 'doctor'
    PROFESSOR = 'professor'

    TITLES = {
        MISTER: _("Mr."),
        MISTRESS: _("Mrs."),
        MISS: _("Miss"),
        DOCTOR: _("Dr."),
        PROFESSOR: _("Pr.")
    }

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = 'desk'
        verbose_name = _("Provider")
        verbose_name_plural = _("Providers")

    username = models.CharField(
        _("username"), max_length=50, primary_key=True,
        help_text=_("Champs obligatoires. 50 caractères ou moins. "
                    "Lettres, chiffres et caractères @ /. / + / - / _"),
        validators=[validators.RegexValidator(re.compile("^[\w.@+-]+$"),
                    _("Enter a valid username."), "invalid")])

    gender = models.CharField(max_length=30, choices=GENDERS.items(),
                              default=UNKNOWN, verbose_name=_("Sexe"))
    title = models.CharField(max_length=50, choices=TITLES.items(),
                             blank=True, null=True, verbose_name=_("Titre"))
    first_name = models.CharField(max_length=100, blank=True, null=True,
                                  verbose_name=_("Prénom"))
    middle_name = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name=_("Middle Name"))
    last_name = models.CharField(max_length=100, blank=True, null=True,
                                 verbose_name=_("Nom"))
    maiden_name = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name=_("Maiden Name"))
    position = models.CharField(max_length=250, blank=True, null=True,
                                verbose_name=_("Position"))
    access_since = models.DateTimeField(default=timezone.now,
                                        verbose_name=_("Access Since"))
    email = models.EmailField(_("email address"), blank=True, null=True)
    phone = models.CharField("Téléphone", max_length=50,
                             blank=True, null=True)
    phone2 = models.CharField("Téléphone 2", max_length=50,
                              blank=True, null=True)
    project = models.ForeignKey("Project", related_name='projects')
    # site = models.ManyToManyField(RegistrationSite, null=True, blank=True)

    is_staff = models.BooleanField(
        _("staff status"), default=False,
        help_text=_("Designates whether the user can "
                    "log into this admin site."))
    is_active = models.BooleanField(
        _("active"), default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    # django manager first
    objects = ProviderManager()
    active = ActiveManager()

    def __str__(self):
        return "{} {}".format(
            self.get_title_full_name(), self.get_access())

    @classmethod
    def get_or_none(cls, username, with_inactive=False):
        qs = cls.objects if with_inactive else cls.active
        try:
            return qs.get(username=username)
        except cls.DoesNotExist:
            return None

    def edite_url(self):
        return reverse("user_change", args=[self.pk])

    def save(self, *args, **kwargs):

        # assign_role(self, Guest)
        author = None
        if 'author' in kwargs.keys():
            author = kwargs.pop('author')

        if 'at' in kwargs.keys():
            at = kwargs.pop('at')
        else:
            at = timezone.now()

        create_revision = False

        try:
            last_version = reversion.get_unique_for_object(self)[0].field_dict
        except (IndexError, AttributeError, TypeError):
            create_revision = True
            last_version = {}

        # for field in ('role', 'site', 'is_active'):
        #     if field == 'is_active':
        #         current_value = getattr(self, field, False)
        #     else:
        #         current_value = getattr(getattr(self, field), 'slug')
        #     if last_version.get(field, current_value) != current_value:
        #         create_revision = True
        #         break

        if create_revision:
            self.access_since = at
            with reversion.create_revision():
                super(Provider, self).save(*args, **kwargs)
                reversion.set_user(author)
        else:
            super(Provider, self).save(*args, **kwargs)

    def history(self):
        version_list = reversion.get_unique_for_object(self)
        updates = []
        for version in reversed(version_list):
            vdata = version.field_dict
            inside_date = vdata.get('access_since')
            updates.append({
                'is_active': vdata.get('is_active'),
                # 'role': Role.get_or_none(vdata.get('role')),
                'site': Entity.get_or_none(vdata.get('site')),
                'from': vdata.get('access_since'),
                # TODO: fix end date of access
                'to': None,
                'access': self.get_access(at=inside_date),
                'name': self.name(at=inside_date)
            })
        return updates

    def name(self, at=None):
        ''' prefered representation of the provider's name at given date '''
        return self.get_complete_name(at=at, with_position=False)

    # TODO: Add history support for string repr.
    def get_complete_name(self, with_position=True, at=None):
        data = self._name_parts()
        data.update({'title_full_name': self.get_title_full_name()})
        name = ugettext("{title_full_name}/{access}").format(**data)
        if not self.position or not self.position.strip() or not with_position:
            return name.strip()
        return ugettext("{name} ({position})") \
            .format(name=name, position=self.position).strip()

    def get_complete_name_position(self, at=None):
        return self.get_complete_name(at=at, with_position=True)

    def get_full_name(self):
        if not self.has_name_infos():
            return self.username.strip()
        return ugettext("{maiden}{first}{middle}{last}") \
            .format(**self._name_parts()).strip()

    def get_title_full_name(self):
        data = self._name_parts()
        data.update({'full_name': self.get_full_name()})
        return ugettext("{title}{full_name}").format(**data).strip()

    def get_short_name(self):
        if not self.has_name_infos():
            return self.username.strip()
        return ugettext("{first_i}{middle_i}{last}") \
            .format(**self._name_parts()).strip()

    def get_title_short_name(self):
        data = self._name_parts()
        data.update({'short_name': self.get_short_name()})
        return ugettext("{title}{short_name}").format(**data).strip()

    def get_access(self, at=None):
        return self.get_roles()
        if not self.is_active:
            return ugettext("Désactivé")
        if not self.site:
            return self.get_roles()
        return ugettext("{role} à {site}").format(
            role=self.get_roles(), site=self.site.name).strip()

    def get_roles(self):
        role = [i.get_name().replace('_', ' ').title() for i in get_user_roles(self)]
        return "" if len(role) == 0 else ",".join(role)

    def has_name_infos(self):
        return (
            self.first_name or self.middle_name or self.last_name or self.maiden_name)

    def email_user(self, subject, message, from_email=None):
        if self.email:
            send_mail(subject, message, from_email, [self.email])

    def is_central(self):
        return self.site.level == 0

    # def last_actions(self):
    #     return Action.last_for(self, limit=10)

    @property
    def is_tech(self):
        return self.role.slug in ('desk_tech', 'desk_admin')

    @property
    def is_admin(self):
        return self.role.slug in ('desk_admin')

    def disable(self):
        self.is_active = False
        self.save()

    def enable(self):
        self.is_active = True
        self.save()

    @classmethod
    def find_by_site(cls, site):
        return cls.active.filter(site__slug=site.slug)

    @classmethod
    def find_at(cls, site=None, slugs=None):
        providers = []
        for rps in slugs:
            providers += list(cls.find_by_role_site(
                role_slug=rps, site=site))
            providers += list(cls.find_by_privilege(priv_slug=rps,
                                                    site=site))
        return list(set(providers))

    def _name_parts(self):
        empty = ""
        return {
            'position': "{}".format(self.position) if self.position else empty,
            'title': "{} ".format(self.TITLES.get(self.title)) if self.title else empty,
            'maiden': "{} "
            .format(self.maiden_name.upper()) if self.maiden_name else empty,
            'first': "{} "
            .format(self.first_name.title()) if self.first_name else empty,
            'first_i': "{}. "
            .format(self.first_name[0].title()) if self.first_name else empty,
            'middle': "{} "
            .format(self.middle_name.title()) if self.middle_name else empty,
            'middle_i': "{} "
            .format(self.middle_name[0].title())
            if self.middle_name else empty,
            'last': "{} "
            .format(self.last_name.upper()) if self.last_name else empty,
            'access': self.get_access(),
        }

reversion.register(Provider)
