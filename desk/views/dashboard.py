#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# from desk.decorators import user_permission
from desk.models.Entities import Entity


@login_required
def user_dashboard(request):
    context = {'page_slug': 'dashboard'}

    return render(request, 'user_dashboard.html', context)
