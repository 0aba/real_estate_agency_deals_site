# Generated by Django 5.1.7 on 2025-04-02 06:19

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('last_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='Фамилия')),
                ('first_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='Имя')),
                ('patronymic', models.CharField(blank=True, max_length=128, null=True, verbose_name='Отчество')),
                ('photo', models.ImageField(blank=True, default='default/photo.jpg', upload_to='photos/user/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name='Фото')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Почта')),
                ('verification_email', models.BooleanField(default=False)),
                ('view_email', models.BooleanField(default=False, verbose_name='Отображать почту')),
                ('phone', models.CharField(blank=True, max_length=16, null=True, validators=[django.core.validators.RegexValidator('^\\+[1-9]\\d{1,14}$', 'Номер телефона должен быть в международном формате E.164 "+{от 2 до 15 цифр}"')], verbose_name='Номер телефона')),
                ('date_register', models.DateTimeField(auto_now_add=True)),
                ('banned', models.BooleanField(default=False)),
                ('online', models.BooleanField(default=False)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('about', models.CharField(blank=True, max_length=512, null=True, verbose_name='О себе')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ConfirmationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('type', models.SmallIntegerField(choices=[(0, 'Email Confirmation'), (1, 'Password Restore')])),
                ('validity_time', models.DurationField(null=True, validators=[django.core.validators.MinValueValidator(datetime.timedelta(0))])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='confirmation_codes_fk', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Код подтверждения',
                'verbose_name_plural': 'Коды подтверждения',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=256)),
                ('event_time', models.DateTimeField(auto_now_add=True)),
                ('link', models.CharField(max_length=512, null=True)),
                ('viewed', models.BooleanField(default=False)),
                ('to_whom', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='notification_fk', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Уведомление',
                'verbose_name_plural': 'Уведомления',
            },
        ),
        migrations.CreateModel(
            name='PrivateMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=256, verbose_name='Сообщение')),
                ('date_write', models.DateTimeField(auto_now_add=True)),
                ('viewed', models.BooleanField(default=False)),
                ('change', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('received_PM', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='received_PM_fk', to=settings.AUTH_USER_MODEL)),
                ('wrote_PM', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='wrote_PM_fk', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Личное сообщение',
                'verbose_name_plural': 'Личные сообщения',
                'ordering': ('-date_write',),
            },
            managers=[
                ('non_deleted', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_add', models.DateTimeField(auto_now_add=True)),
                ('who_on_BL', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='who_on_BL_fk', to=settings.AUTH_USER_MODEL)),
                ('whose_BL', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='whose_BL_fk', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Человек в ЧС',
                'verbose_name_plural': 'Люди в ЧС',
                'unique_together': {('whose_BL', 'who_on_BL')},
            },
        ),
    ]
