#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging

from django.db import models

# from snisi_tools.misc import get_uuid

logger = logging.getLogger(__file__)


# def get_temp_receipt(instance):
#     return 'uuid:{uuid}'.format(uuid=get_uuid())


class ActiveManager(models.Manager):

    def get_queryset(self):
        return super(ActiveManager, self).get_queryset() \
                                         .filter(is_active=True)
