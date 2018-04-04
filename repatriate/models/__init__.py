#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging

from repatriate.models.settings import Settings
from repatriate.models.collects import Collect
from repatriate.models.targets import Target, OrganizationTarget, TargetTypeAssistance
from repatriate.models.persons import Person, ContactTemoin, VulnerabilityPerson
from repatriate.models.others import (
    Activite, Lien, NiveauxScolaire, Lien, TypeAssistance, Activite,
    Organization, Camp, Vulnerability)

logger = logging.getLogger(__name__)