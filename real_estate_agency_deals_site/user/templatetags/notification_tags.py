from user.models import Notification
from django import template

register = template.Library()

UNREAD_MESSAGES_CACHE_TIMEOUT = 60

@register.simple_tag
def get_notifications(user):
    if user.is_anonymous:
        return []

    queryset = Notification.objects.filter(
        to_whom=user,
    ).order_by('viewed', '-event_time')

    return queryset


@register.filter
def has_viewed(notifications):
    return any(not notification.viewed for notification in notifications)

