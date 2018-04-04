#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
# from desk.decorators import user_permission
from desk.models import Entity, Provider
from desk.forms import (UserCreationForm, UserChangeForm)


@login_required
def user_manager(request):
    # members = Provider.objects.filter(is_admin=False)
    members = Provider.objects.all()

    for member in members:
        # print(member)
        member.url_change = reverse("user_change", args=[member.pk])

    user = request.user
    if request.method == 'POST' and '_notice_new' in request.POST:
        _form = UserCreationForm(request.POST or None)
        if _form.is_valid():
            # notice = _form.save(commit=False)
            # notice.author = Member.objects.filter()
            # notice.save()
            return redirect("/")
    else:
        _form = UserCreationForm()
    cxt = {'members': members, 'user': user, '_form': _form}
    return render(request, 'user_manager.html', cxt)


@login_required
def user_new(request):
    print(request.user)
    if request.method == 'POST' and '_user_new' in request.POST:
        user_new_form = UserCreationForm(request.POST or None)
        if user_new_form.is_valid():
            user_new_form.save()
            return redirect("/home")
    else:
        user_new_form = UserCreationForm()
    cxt = {"user_new_form": user_new_form}
    return render(request, 'user_new.html', cxt)


@login_required
def user_change(request, *args, **kwargs):
    id_url = kwargs["pk"]

    selected_member = Provider.objects.get(pk=id_url)
    if request.method == 'POST' and '_user_change' in request.POST:
        user_change_form = UserChangeForm(request.POST,
                                          instance=selected_member)
        if user_change_form.is_valid():
            user_change_form.save()
            return redirect("/user_manager")
    else:
        user_change_form = UserChangeForm(instance=selected_member)
    cxt = {"user_change_form": user_change_form}
    return render(request, 'user_change.html', cxt)
