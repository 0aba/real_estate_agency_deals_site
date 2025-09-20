from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from user.models import User


class Command(BaseCommand):
    help = 'Changes the superuser status to the opposite of the given user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user whose superuser status needs to be changed to the opposite')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        try:
            user_action = User.objects.get(username=username)
            user_action.is_superuser = not user_action.is_superuser
            user_action.save()
            action_status = 'promoted to superuser' if user_action.is_superuser else 'demoted from superuser'
            self.stdout.write(self.style.SUCCESS(f'User {username} has been {action_status}.'))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found.'))
