#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json
import logging

import reversion
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
# from collections import OrderedDict


logger = logging.getLogger(__name__)


_s = lambda l: sorted(l, key=lambda e: e.name)


class Project(models.Model):

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(max_length=200)
    desciption = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{name}".format(name=self.name)


class RegistrationSite(models.Model):

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(max_length=200)
    project = models.ForeignKey("Project", blank=True, null=True, related_name='entity_projects')
    active = models.BooleanField(default=True)
    locality = TreeForeignKey("Entity", null=True, related_name="site_localities")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)
    confirmed = models.BooleanField(default=True)

    def __str__(self):
        return "{name} / {locality}".format(
            name=self.name, locality=self.locality)

    def active(self):
        return self.filter(active=True)


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
    short_name = models.CharField(
        _("Name"), max_length=10, null=True, blank=True)

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

    slug = models.SlugField(_("Slug"), max_length=50, primary_key=True)
    name = models.CharField(_("Name"), max_length=50)
    type = models.ForeignKey(EntityType, related_name='entities',
                             verbose_name=_("Type"))
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            verbose_name=_("Parent"))
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    modified_on = models.DateTimeField(default=timezone.now)

    objects = TreeManager()
    manager = EntityQuerySet.as_manager()

    def __str__(self):
        return self.name

    @classmethod
    def get_or_none(cls, slug, type_slug=None):
        try:
            if type_slug is not None:
                return cls.objects.get(slug=slug,
                                       type__slug=type_slug).casted()
            return cls.objects.get(slug=slug).casted()
        except cls.DoesNotExist:
            return None

    @property
    def geojson(self):
        if not self.geometry:
            if self.latitude and self.longitude:
                return {"type": "Point",
                        "coordinates": [self.longitude, self.latitude]}
            return {}
        return json.loads(self.geometry)

    @property
    def geojson_feature(self):
        feature = {
            "type": "Feature",
            "properties": self.to_dict()
        }
        if self.geojson:
            feature.update({"geometry": self.geojson})
        return feature

    @property
    def is_central(self):
        return self.level == 0

    def to_dict(self):
        return {'slug': self.slug,
                'name': self.name,
                'display_typed_name': self.display_typed_name(),
                'display_code_name': self.display_code_name(),
                'display_full_name': self.display_full_name(),
                'display_full_typed_name': self.display_full_typed_name(),
                'type': self.type.slug,
                'parent': getattr(self.parent, 'slug', None),
                'latitude': self.latitude,
                'longitude': self.longitude,
                'active': self.active}

    def display_name(self):
        return self.name.upper()

    def display_full_name(self):
        if self.parent and self.parent.parent:
            if self.type.slug == 'health_center':
                parent = self.get_health_district()
            else:
                parent = self.parent
            return ugettext("{name}/{parent}").format(
                name=self.display_name(),
                parent=parent.display_name())
        return self.display_name()

    def display_code_name(self):
        return ugettext("{name} ({code})").format(
            code=self.slug, name=self.display_name())

    def display_typed_name(self):
        if self.type.slug != 'country':
            return ugettext("{type} de {name}").format(
                type=self.type.name, name=self.name)
        return self.display_name()

    def display_typed_short_name(self):
        if self.type.slug != 'country':
            return ugettext("{type} {name}").format(
                type=self.type.short_name, name=self.name)
        return self.display_name()

    def display_full_typed_name(self):
        if self.type.slug != 'country':
            return ugettext("{type} de {name}").format(
                type=self.type.name, name=self.display_full_name())
        return self.display_name()

    def display_full_typed_short_name(self):
        if self.type.slug != 'country':
            return ugettext("{type} {name}").format(
                type=self.type.short_name, name=self.display_full_name())
        return self.display_name()

    def parent_level(self):
        if self.parent:
            return self.parent.type
        # return self.parent
        return "NO PARENT"

    @property
    def gps(self):
        if self.latitude is not None and self.longitude is not None:
            return "{lat},{lon}".format(lat=self.latitude, lon=self.longitude)

    # def all_children(self, health_only=False):
    #     if self.type.slug == 'health_center':
    #         qs = AdministrativeEntity.manager.active().filter(
    #             health_entity=self)
    #     else:
    #         qs = self.children.all()
    #         if health_only:
    #             qs = qs.filter(type__slug__startswith='health_')
    #     return qs

    def get_type(self, type_slug):
        return getattr(self, 'get_{}'.format(type_slug), lambda: None)()

    def get_types(self, type_slug):
        return getattr(self, 'get_{}s'.format(type_slug), lambda: [])()

    def get_natural_children(self, skip_slugs=[]):
        _clean_list = lambda l, sl: [slug for slug in l if slug not in sl]

        lineage = _clean_list(['country',
                               'health_region', 'health_district',
                               'health_area',
                               ['health_center', 'vfq']], skip_slugs)

        admin_lineage = _clean_list(['country',
                                     'region', 'cercle',
                                     'commune', 'vfq'], skip_slugs)

        ts = self.casted().type.slug
        if ts not in lineage and ts not in admin_lineage:
            return []

        if ts in lineage:
            child_ts = lineage[lineage.index(ts) + 1]
        else:
            child_ts = admin_lineage[admin_lineage.index(ts) + 1]

        if not isinstance(child_ts, list):
            child_ts = _clean_list([child_ts], skip_slugs)

        children = []
        for cts in child_ts:
            for e in getattr(self, 'get_{}s'.format(cts), [])():
                children.append(e)
        return _s(children)

    def get_natural_parent(self, skip_slugs=[]):
        _clean_list = lambda l, sl: [slug for slug in l if slug not in sl]

        lineage = _clean_list(['country',
                               'health_region', 'health_district',
                               'health_area',
                               'health_center', 'vfq'], skip_slugs)

        admin_lineage = _clean_list(['country',
                                     'region', 'cercle',
                                     'commune', 'vfq'], skip_slugs)

        ts = self.casted().type.slug
        if ts not in lineage and ts not in admin_lineage:
            return None

        if ts in lineage:
            parent_ts = lineage[lineage.index(ts) - 1]
        else:
            parent_ts = admin_lineage[admin_lineage.index(ts) - 1]

        return getattr(self, 'get_{}'.format(parent_ts), lambda: None)()

    def get_country(self):
        return Entity.manager.active().get(type__slug='country')

    def get_vfq(self):
        if self.type.slug == 'vfq':
            return self.casted()

        return None

    def get_commune(self):
        # commune
        # vfq
        t = self.type.slug
        if t == 'commune':
            return self.casted()

        if t in ('vfq',):
            return self.parent.casted()

        return None

    def get_cercle(self):
        # cercle
        # commune
        # vfq
        t = self.type.slug
        if t == 'cercle':
            return self.casted()

        if t in ('vfq', 'commune'):
            return self.get_commune().parent.casted()

        return None

    def get_region(self):
        # region
        # cercle
        # commune
        # vfq
        t = self.type.slug
        if t == 'region':
            return self.casted()

        if t in ('vfq', 'commune', 'cercle'):
            return self.get_cercle().parent.casted()

        return None

    def get_vfqs(self):
        # country
        # health_region
        # health_district
        # health_center
        t = self.type.slug
        if t in ('country', 'region', 'cercle'):
            return _s([e for area in self.get_communes()
                       for e in area.get_vfqs()])
        if t in ('country', 'health_region',
                 'health_district', 'health_center'):
            return _s([e for area in self.get_health_areas()
                       for e in area.get_vfqs()])
        if t == 'health_area':
            return _s(list(AdministrativeEntity.manager.active().filter(
                type__slug='vfq', health_entity__slug=self.slug)))
        if t == 'commune':
            return _s([e.casted() for e in self.get_children().filter(
                active=True, type__slug='vfq')])
        if t == 'vfq':
            return _s([self.casted()])
        return []

    def get_communes(self):
        # country
        # health_region
        # health_district
        # health_center
        t = self.type.slug
        if t in ('country', 'region', 'health_region', 'health_district',
                 'health_area', 'health_center'):
            return _s([e for area in self.get_cercles()
                       for e in area.get_communes()])
        if t == 'cercle':
            return _s([e.casted() for e in self.get_children().filter(
                active=True, type__slug='commune')])
        if t == 'commune':
            return _s([self.casted()])
        return []

    def get_cercles(self):
        # country
        # health_region
        # health_district
        # health_center
        t = self.type.slug
        if t in ('country', 'health_region', 'health_district',
                 'health_area', 'health_center'):
            return _s([e for area in self.get_regions()
                       for e in area.get_cercles()])
        if t == 'region':
            return _s([e.casted() for e in self.get_children().filter(
                active=True, type__slug='cercle')])
        if t == 'cercle':
            return _s([self.casted()])
        return []

    def get_regions(self):
        t = self.type.slug
        if t == 'region':
            return _s([self.casted()])
        root = Entity.manager.active().get(level=0)
        return _s([e.casted() for e in root.get_children().filter(
            active=True, type__slug='region')])

    def get_descendants_of(self, type_slug=None,
                           include_self=False,
                           ascending=False):
        qs = self.get_descendants(include_self=include_self)
        if type_slug is not None:
            qs.filter(type__slug=type_slug)

        return [e.casted() for e in qs]

    def get_ascendants_of(self, type_slug=None,
                          include_self=False, ascending=False):
        qs = self.get_ascendants(include_self=include_self)
        if type_slug is not None:
            qs.filter(type__slug=type_slug)
        return qs

    def casted(self, hard=True):
        if self.type.slug == 'country':
            cls = Entity
        elif self.type.slug in ['region', 'cercle', 'commune', 'vfq']:
            cls = AdministrativeEntity
        else:
            cls = Entity

        # might already be of correct type.
        if self.__class__ == cls:
            return self

        # recreate complete object off database.
        # required to access per-type properties/fields
        if hard:
            return cls.get_or_none(self.slug)

        # lazy type cast
        self.__class__ = cls

        return self


class AdministrativeEntity(Entity):

    class Meta:
        app_label = 'desk'
        verbose_name = _("Admin. Entity")
        verbose_name_plural = _("Admin. Entities")

    # health_entity = models.ForeignKey(HealthEntity, blank=True, null=True,
    #                                   related_name='admin_entities')
    main_entity_distance = models.FloatField(blank=True, null=True)

    objects = TreeManager()
    manager = EntityQuerySet.as_manager()

reversion.register(Entity)
