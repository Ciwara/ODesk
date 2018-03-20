#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
from rolepermissions.permissions import register_object_checker
from OIMDesk.roles import DNDSTech


@register_object_checker()
def access_locality(role, user, local):
    if role == DNDSTech:
        return True

    if user.local == local:
        return True

    return False