#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from desk.models import Provider
from desk.forms import (UserCreationForm, UserChangeForm)
# from rolepermissions.decorators import has_role_decorator
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def user_manager(request):
    members = Provider.objects.filter(is_staff=False)
    # members = Provider.objects.all()

    user = request.user

    cxt = {'members': members, 'user': user}
    return render(request, 'user_manager.html', cxt)


@login_required
# @has_role_decorator("DeskAssistantAdmin")
def user_new(request):
    if request.method == 'POST' and '_user_new' in request.POST:
        user_new_form = UserCreationForm(request.POST or None)
        if user_new_form.is_valid():
            user_new_form.save()
            return redirect("/user-manager")
    else:
        user_new_form = UserCreationForm()
    cxt = {"user_new_form": user_new_form}
    return render(request, 'user_new.html', cxt)


@login_required
def user_change(request, *args, **kwargs):
    id_url = kwargs["pk"]
    selected_member = Provider.objects.get(pk=id_url)
    if request.method == 'POST' and '_user_change' in request.POST:
        user_change_form = UserChangeForm(
            request.POST, instance=selected_member)
        if user_change_form.is_valid():
            user_change_form.save()
            return redirect("/user-manager")
    else:
        user_change_form = UserChangeForm(instance=selected_member)
    cxt = {"user_change_form": user_change_form}
    return render(request, 'user_change.html', cxt)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès!')
            return redirect('home')
        else:
            messages.error(request, "Veuillez corriger l'erreur ci-dessous.")
        print(messages)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })
