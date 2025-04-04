from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone


@receiver(user_logged_in)
def set_user_online(sender, request, user, **kwargs):
    user.online = True
    user.save()


@receiver(user_logged_out)
def set_user_offline(sender, request, user, **kwargs):
    user.online = False
    user.last_seen = timezone.now()
    user.save()
