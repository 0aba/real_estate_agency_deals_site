from user.models import PrivateMessage
from django.core.cache import cache
from django import template

register = template.Library()

UNREAD_MESSAGES_CACHE_TIMEOUT = 60

@register.simple_tag
def get_unread_count(user):
    if user.is_anonymous:
        return 0

    cache_key = f'unread_messages_exists_{user.id}'
    unread_count = cache.get(cache_key)

    if unread_count is None:
        unread_count = PrivateMessage.non_deleted.filter(
            received_PM=user,
            viewed=False,
        ).count()
        cache.set(cache_key, unread_count, UNREAD_MESSAGES_CACHE_TIMEOUT)

    return unread_count
