from django.core.management.base import BaseCommand
from django.db import IntegrityError
from user.models import User
import getpass
import uuid


class Command(BaseCommand):
    help = 'Create user with verification email for testing site'

    def handle(self, *args, **kwargs):
        username = input('Enter your username: ')
        password = getpass.getpass('Enter your password: ')
        confirm_password = getpass.getpass('Confirm your password: ')

        if password != confirm_password:
            self.stdout.write(self.style.ERROR('Passwords do not match'))
            return

        try:
            User.objects.create_user(username=username, password=password, email=f'{str(uuid.uuid4())[:8]}@fake.fake', verification_email=True)
            self.stdout.write(self.style.SUCCESS('User created successfully'))
        except IntegrityError as e:
            if '(username)=' in str(e):
                self.stdout.write(self.style.ERROR('Error: username already exists'))
            elif '(email)=' in str(e):
                self.stdout.write(self.style.WARNING('Warning: the generated email already existed, which is why the account was not created'))
            else:
                self.stdout.write(self.style.ERROR('Error: could not create user due to an integrity error'))
