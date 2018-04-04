#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from desk.models.Entities import Entity


def index(request):
    context = {'page_slug': 'index'}

    return render(request, 'index.html', context)


@login_required
def dashboard(request):
    print("dashboard")
    context = {'page_slug': 'dashboard'}

    return render(request, 'home.html', context)
