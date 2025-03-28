from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from user.models import Notification


@require_POST
@login_required
def mark_notification_viewed(request, notification_id):
    try:
        Notification.objects.filter(id=notification_id, to_whom=request.user).update(viewed=True)
        return JsonResponse({'message': 'Notification marked as viewed'}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

@require_POST
@login_required
def delete_notification(request, notification_id):
    try:
        Notification.objects.get(id=notification_id, to_whom=request.user).delete()
        return JsonResponse({'message': 'Notification deleted'}, status=200) # INFO! 204 не обрабатывается адекватно ((
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)
