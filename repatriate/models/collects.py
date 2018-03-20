#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import logging
# from collections import OrderedDict
from statistics import median, StatisticsError

from django.db import models
# from django.urls import reverse
from django.conf import settings
# from django.utils import timezone

from desk.utils import gen_targets_csv
from repatriate.models.targets import Target
# from desk.models.settings import Settings

logger = logging.getLogger(__name__)


class Collect(models.Model):

    class Meta:
        ordering = ['started_on', ]

    name = models.CharField(max_length=40)
    started_on = models.DateTimeField(auto_now_add=True)
    ona_form_pk = models.IntegerField(blank=True, null=True)
    nb_submissions = models.IntegerField(blank=True, null=True)
    nb_medias_form = models.IntegerField(blank=True, null=True)
    nb_medias_scan_form = models.IntegerField(blank=True, null=True)
    medias_size_form = models.IntegerField(blank=True, null=True)
    medias_size_scan_form = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()

    def to_dict(self):
        data = {}

        for dkey in ('started_on', 'ended_on', 'finalized_on', 'uploaded_on'):
            if getattr(self, dkey):
                data.update({dkey: getattr(self, dkey).isoformat()})

        for key in ('cercle_id', 'commune_id', 'suffix',
                    'ona_form_pk', 'ona_scan_form_pk',
                    'nb_submissions', 'nb_indigents', 'nb_non_indigents',
                    'nb_medias_form', 'nb_medias_scan_form',
                    'medias_size_form', 'medias_size_scan_form'):
            data.update({key: getattr(self, key)})

        data.update({
            'cercle': self.cercle,
            'commune': self.commune,
            'mayor': {
                'title_code': self.mayor_title,
                'title': self.verbose_mayor_title,
                'name': self.mayor_name,
            },
            'ona_form_id': self.ona_form_id(),
            'ona_scan_form_id': self.ona_scan_form_id(),
        })
        return data

    def form_title(self):
        return "Enquête rapatriment"

    def ona_form_id(self):
        return self.ona_form_pk

    @property
    def nb_medias(self):
        return sum([self.nb_medias_form or 0])

    @property
    def medias_size(self):
        return sum([self.medias_size_form or 0])

    @classmethod
    def get_or_none(cls, cid):
        try:
            return cls.objects.get(id=cid)
        except cls.DoesNotExist:
            return None

    def __str__(self):
        return self.name

    @property
    def previous_verbose_status(self):
        try:
            assert self.sm_index > 0
            return self.machine_value_for(self.sm_index - 1)[0]
        except:
            return "Supprimer la collecte"

    @property
    def uploaded(self):
        return self.uploaded_on is not None

    def has_ended(self):
        return self.status in (self.ENDED, self.FINALIZED)

    def has_finalized(self):
        return self.status == self.FINALIZED

    @property
    def sm_index(self):
        try:
            return self.machine_index_for(self.status)
        except ValueError:
            return -1

    def process_form_data(self, data):
        from desk.ona import get_media_size

        nb_medias = 0
        medias_size = 0
        for submission in data:
            # get attachement filesizes
            attachments = submission.get('_attachments', [])
            for media in attachments:
                media['filesize'] = get_media_size(
                    media.get('filename', ''))
            submission['_attachments'] = attachments

            # create Target
            Target.create_from_submission(self, submission)

            nb_medias += len(attachments)
            medias_size += sum([m['filesize'] for m in attachments])

        self.nb_submissions = len(data)
        self.nb_medias_form = nb_medias
        self.medias_size_form = medias_size
        self.save()

    def reset_form_data(self, delete_submissions=False):
        for target in self.targets.all():
            target.remove_completely(delete_submissions=delete_submissions)
        self.nb_submissions = None
        self.nb_medias_form = None
        self.medias_size_form = None
        self.save()

    def get_targets_csv(self):
        return gen_targets_csv(self.targets.all())

    def get_documents_path(self):
        return os.path.join(settings.COLLECT_DOCUMENTS_FOLDER,
                            self.ona_form_id())

    def get_nb_men(self):
        return self.targets.filter(gender=Target.MALE).count()

    def get_nb_women(self):
        return self.targets.filter(gender=Target.FEMALE).count()

    def get_median_age(self):
        try:
            return median([t['age'] for t in self.targets.values('age')])
        except StatisticsError:
            return None

    def get_nb_papers(self):
        return self.nb_submissions * 3 if self.nb_submissions else None

    def export_data(self):
        data = self.to_dict().copy()
        data.update({
            'targets': [t.export_data() for t in self.targets.all()]
        })
        return data
