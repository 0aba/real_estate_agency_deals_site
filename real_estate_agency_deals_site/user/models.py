from django.core.validators import FileExtensionValidator, RegexValidator, MinValueValidator, MaxValueValidator
from real_estate_agency_deals_site.settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.utils import timezone
from django.db import models
from uuid import uuid4


class User(AbstractUser):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    last_name = models.CharField(null=True, blank=True, max_length=128, verbose_name='Фамилия')
    first_name = models.CharField(null=True, blank=True, max_length=128, verbose_name='Имя')
    patronymic = models.CharField(null=True, blank=True, max_length=128, verbose_name='Отчество')

    photo = models.ImageField(blank=True, upload_to='photos/user/%Y/%m/%d/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    ], default='default/photo.jpg', verbose_name='Фото')

    email = models.EmailField(unique=True, verbose_name='Почта')
    verification_email = models.BooleanField(default=False)
    view_email = models.BooleanField(default=False, verbose_name='Отображать почту')
    phone = models.CharField(null=True, blank=True, validators=[
        RegexValidator(r'^\+[1-9]\d{1,14}$', 'Номер телефона должен быть в международном формате E.164'
                                                  ' "+{от 2 до 15 цифр}"')
    ], max_length=16, verbose_name='Номер телефона')
    date_register = models.DateTimeField(auto_now_add=True)
    banned = models.BooleanField(default=False)
    online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    about = models.TextField(null=True, blank=True, max_length=512, verbose_name='О себе')

    objects = UserManager()


class ConfirmationCode(models.Model):
    class Meta:
        verbose_name = 'Код подтверждения'
        verbose_name_plural = 'Коды подтверждения'

    class ConfirmationCodeType(models.IntegerChoices):
        EMAIL_CONFIRMATION = 0
        PASSWORD_RESTORE = 1

    code = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='confirmation_codes_fk')
    type = models.SmallIntegerField(choices=ConfirmationCodeType.choices)
    validity_time = models.DurationField(null=True, validators=[MinValueValidator(timezone.timedelta(0))])
    date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()


class Notification(models.Model):
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    to_whom = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='notification_fk')
    message = models.CharField(max_length=256)
    event_time = models.DateTimeField(auto_now_add=True)
    color = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(16777215)])
    link = models.CharField(null=True, max_length=512)
    viewed = models.BooleanField(default=False)

    objects = models.Manager()


class PrivateMessage(models.Model):
    class Meta:
        verbose_name = 'Личное сообщение'
        verbose_name_plural = 'Личные сообщения'

    wrote_PM = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='wrote_PM_fk')
    received_PM = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='received_PM_fk')
    message = models.CharField(max_length=256, verbose_name='Сообщение')
    date_write = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)
    change = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class NonDeletedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(deleted=False)

    non_deleted = NonDeletedManager()
    objects = models.Manager()


class BlackList(models.Model):
    class Meta:
        verbose_name = 'Человек в ЧС'
        verbose_name_plural = 'Люди в ЧС'
        unique_together = (('whose_BL', 'who_on_BL'),)

    whose_BL = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='whose_BL_fk')
    who_on_BL = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='who_on_BL_fk')
    date_add = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
