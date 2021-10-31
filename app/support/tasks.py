import logging

from celery import shared_task
from django.core.mail import send_mail

from .models import User


@shared_task
def send_email(user_id, data):
    try:
        user = User.objects.get(pk=user_id)
        send_mail(
            'Support message',
            data,
            'dimaformago281@gmail.com',
            [user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        logging.warning("Tried to send verification email to non-existing user '%s'" % user_id)
