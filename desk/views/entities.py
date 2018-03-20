#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required

from desk.models.Entities import Entity


@login_required
def entities_list(request, **kwargs):

    return redirect('entity_profile', entity_slug='mali')


@login_required
def entity_profile(request, entity_slug, **kwargs):
    context = {}

    entity = Entity.get_or_none(entity_slug)
    if entity is None:
        raise Http404("No Entity for slug {}".format(entity_slug))

    context.update({'entity': entity})

    return render(request,
                  kwargs.get('template_name', "entity_profile.html"),
                  context)
