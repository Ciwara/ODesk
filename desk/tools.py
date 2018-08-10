#!/usr/bin/env python
# encoding=utf-8
# vim: ai ts=4 sts=4 et sw=4 nu
import os
from django.conf import settings
from datetime import datetime
# from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage


def share_by_mail(sender, instance, *args, **kwargs):

    from_email = settings.EMAIL_HOST_USER

    try:
        msg = EmailMessage(
            instance.subject, instance.msg_body, from_email,
            settings.EMAIL_TO_PARTNER)
        msg.content_subtype = "html"
        if instance.with_media:
            msg.attach_file(
                os.path.join(settings.MEDIA_ROOT, instance.media_file))
        msg.send()
    except Exception as e:
        print(e)


def str_to_date(str_date):
    return datetime.strptime(str_date, "%d/%m/%Y")
