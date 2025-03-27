from django.core.management.base import BaseCommand
from django.db import IntegrityError
from user.models import User
import getpass


class Command(BaseCommand):
    help = 'Create user with verification email for testing site'

    def handle(self, *args, **kwargs):
        username = input('Enter your username: ')
        password = getpass.getpass('Enter your password: ')
        confirm_password = getpass.getpass('Confirm your password: ')
        fake_email = input('Enter your fake email: ')

        if password != confirm_password:
            self.stdout.write(self.style.ERROR('Passwords do not match'))
            return
        try:
            User.objects.create_user(username=username, password=password, email=fake_email, verification_email=True)
        except IntegrityError as e:
            if '(username)=' in str(e):
                self.stdout.write(self.style.ERROR('Error: username already exists'))
            elif '(email)=' in str(e):
                self.stdout.write(self.style.ERROR('Error: email already exists'))
            else:
                self.stdout.write(self.style.ERROR('Error: could not create user due to an integrity error'))
            return

        self.stdout.write(self.style.SUCCESS('User created successfully'))
