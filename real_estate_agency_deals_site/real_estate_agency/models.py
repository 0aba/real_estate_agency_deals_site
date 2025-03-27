from django.core.validators import FileExtensionValidator, RegexValidator, MinValueValidator, MaxValueValidator
from real_estate_agency_deals_site.settings import AUTH_USER_MODEL
from django.utils import timezone
from django.db import models


class RealEstateAgency(models.Model):
    class Meta:
        verbose_name = 'Агенство недвижимости'
        verbose_name_plural = 'Агентства недвижимости'

    logo = models.ImageField(blank=True, upload_to='photos/real_estate_agency/%Y/%m/%d/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    ], default='default/real_estate_agency.jpg', verbose_name='Логотип')
    name = models.CharField(max_length=256, unique=True, verbose_name='Название организации')
    INN = models.CharField(max_length=12, validators=[
        RegexValidator(r'^\d{10,12}$')
    ], unique=True, verbose_name='ИНН')
    about = models.TextField(null=True, blank=True, max_length=512, verbose_name='О агенстве')
    date_registered = models.DateTimeField(auto_now_add=True)
    representative = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='representative_fk')

    objects = models.Manager()


class ReviewAgency(models.Model):
    class Meta:
        verbose_name = 'Отзыв агентства'
        verbose_name_plural = 'Отзывы агенств'

    review_agency = models.ForeignKey(RealEstateAgency, on_delete=models.PROTECT,
                                      related_name='review_agency_fk')
    wrote_review = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                                     related_name='wrote_review_fk')
    message = models.CharField(max_length=256, verbose_name='Отзыв')
    grade = models.DecimalField(max_digits=2, decimal_places=1, default=0.0, validators=[
        MinValueValidator(0.0),
        MaxValueValidator(5.0)
    ], verbose_name='Оценка')
    change = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class NonDeletedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(deleted=False)

    non_deleted = NonDeletedManager()
    objects = models.Manager()


class Realtor(models.Model):
    class Meta:
        verbose_name = 'Релайтер'
        verbose_name_plural = 'Релайтеры'

    last_name = models.CharField(max_length=128, verbose_name='Фамилия')
    first_name = models.CharField(max_length=128, verbose_name='Имя')
    patronymic = models.CharField(null=True, blank=True, max_length=128, verbose_name='Отчество')
    photo = models.ImageField(blank=True, upload_to='photos/realtor/%Y/%m/%d/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    ], default='default/realtor.jpg', verbose_name='Фото')
    experience = models.SmallIntegerField(default=0, validators=[MinValueValidator(0)])
    phone = models.CharField(validators=[
        RegexValidator(r'^\+[1-9]\d{1,14}$', 'Номер телефона должен быть в международном формате E.164'
                                                  ' "+{от 2 до 15 цифр}"')
    ], max_length=16, verbose_name='Номер телефона')
    email = models.EmailField(verbose_name='Почта')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        verbose_name='Цена услуг'
    )
    license = models.CharField(max_length=128, unique=True, verbose_name='Лицензия')
    agency_realtor = models.OneToOneField(RealEstateAgency, on_delete=models.PROTECT, related_name='agency_realtor_fk')

    objects = models.Manager()


class Address(models.Model):
    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    city = models.CharField(max_length=128, verbose_name='Город')
    district = models.CharField(null=True, blank=True, max_length=128, verbose_name='Район')
    street = models.CharField(max_length=128, verbose_name='Улица')
    apartment = models.SmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1)],
                                         verbose_name='Квартира')

    objects = models.Manager()


class RealEstate(models.Model):
    class Meta:
        verbose_name = 'Недвижимость'
        verbose_name_plural = 'Недвижимости'

    class RealEstateType(models.IntegerChoices):
        APARTMENT = 0
        HOUSE = 1
        PLOT = 2

    type = models.SmallIntegerField(choices=RealEstateType.choices, verbose_name='Тип недвижимости')
    main_photo = models.ImageField(upload_to='photos/real_estate/%Y/%m/%d/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    ], verbose_name='Главное фото')
    square = models.SmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Общая площадь')
    when_added = models.DateTimeField(auto_now_add=True)
    about = models.TextField(null=True, blank=True, max_length=512, verbose_name='О недвижимости')
    agency_real_estate = models.ForeignKey(RealEstateAgency, on_delete=models.PROTECT,
                                           related_name='agency_real_estate_fk')
    address_real_estate = models.ForeignKey(Address, null=True, blank=True, on_delete=models.PROTECT,
                                            related_name='address_real_estate_fk')
    deleted = models.BooleanField(default=False)

    class NonDeletedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(deleted=False)

    non_deleted = NonDeletedManager()
    objects = models.Manager()


class PhotoRealEstate(models.Model):
    class Meta:
        verbose_name = 'Фото недвижимости'
        verbose_name_plural = 'Фотографии недвижимости'

    additional_photo_real_estate = models.ForeignKey(RealEstateAgency, on_delete=models.PROTECT,
                                                     related_name='additional_photo_RE_fk')
    photo = models.ImageField(upload_to='photos/real_estate/%Y/%m/%d/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    ], verbose_name='Дополнительная фотография')

    objects = models.Manager()


class DataPlot(models.Model):
    class Meta:
        verbose_name = 'Данные участка'
        verbose_name_plural = 'Данные участков'

    real_estate_DP = models.OneToOneField(RealEstateAgency, on_delete=models.PROTECT, related_name='real_estate_DP_fk')
    buildings = models.BooleanField(verbose_name='Есть постройки')
    communications = models.BooleanField(verbose_name='Есть коммуникации')

    objects = models.Manager()


class DataApartment(models.Model):
    class Meta:
        verbose_name = 'Данные квартиры'
        verbose_name_plural = 'Данные квартир'

    real_estate_DA = models.OneToOneField(RealEstateAgency, on_delete=models.PROTECT, related_name='real_estate_DA_fk')
    number_storeys = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Количество этажей')
    floor = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Этаж')
    balcony = models.BooleanField(verbose_name='Есть балкон')
    furniture = models.BooleanField(verbose_name='Есть мебель')
    year_construction = models.SmallIntegerField(validators=[MinValueValidator(1900)], verbose_name='Год постройки')
    accident_rate = models.BooleanField(verbose_name='Здание аварийное')

    objects = models.Manager()


class DataHouse(models.Model):
    class Meta:
        verbose_name = 'Данные дома'
        verbose_name_plural = 'Данные домов'

    real_estate_DH = models.ForeignKey(RealEstateAgency, on_delete=models.PROTECT, related_name='real_estate_DH_fk')
    number_storeys = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Количество этажей')
    house_area = models.SmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Площадь дома')
    year_construction = models.SmallIntegerField(validators=[MinValueValidator(1900)], verbose_name='Год постройки дома')
    garage = models.BooleanField(verbose_name='Есть гараж')
    communications = models.BooleanField(verbose_name='Есть коммуникации')

    objects = models.Manager()


class Deal(models.Model):
    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'

    class DealType(models.IntegerChoices):
        SALE = 0
        RENT = 1
        CONSTRUCTION = 2

    title = models.CharField(max_length=256, unique=True, verbose_name='Заголовок сделки')
    type = models.SmallIntegerField(choices=DealType.choices, verbose_name='Тип сделки')
    phone = models.CharField(validators=[
        RegexValidator(r'^\+[1-9]\d{1,14}$', 'Номер телефона должен быть в международном формате E.164'
                                                  ' "+{от 2 до 15 цифр}"')
    ], max_length=16, verbose_name='Номер телефона')
    email = models.EmailField(verbose_name='Почта')
    date_create = models.DateTimeField(auto_now_add=True)
    real_estate_deal = models.ForeignKey(RealEstate, on_delete=models.PROTECT, related_name='real_estate_deal_fk')
    deleted = models.BooleanField(default=False)

    class NonDeletedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(deleted=False)

    non_deleted = NonDeletedManager()
    objects = models.Manager()


class DataConstruction(models.Model):
    class Meta:
        verbose_name = 'Данные постройки'
        verbose_name_plural = 'Данные построек'

    deal_construction = models.ForeignKey(Deal, on_delete=models.PROTECT, related_name='deal_construction_fk')
    construction_company = models.CharField(max_length=256, verbose_name='Строительная компания')
    approximate_dates = models.DurationField(null=True, blank=True,
                                             validators=[MinValueValidator(timezone.timedelta(0))],
                                             verbose_name='Примерный срок строительства')
    project_document = models.FileField(upload_to='documents/%Y/%m/%d/', validators=[
        FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'odt']),
    ], verbose_name='Документ проекта')

    objects = models.Manager()


class DataRental(models.Model):
    class Meta:
        verbose_name = 'Данные аренды'
        verbose_name_plural = 'Данные аренд'

    deal_rental = models.ForeignKey(Deal, on_delete=models.PROTECT, related_name='deal_rental_fk')
    price_housing_and_municipalities = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                                           validators=[
                                                               MinValueValidator(0.0),
                                                           ], verbose_name='Цена ЖКХ')
    prepayment = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                     validators=[
                                         MinValueValidator(0.0),
                                     ], verbose_name='Предоплата')
    rental_period_days = models.SmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Срок аренды')
    rented = models.BooleanField(default=False, verbose_name='Арендуется')

    objects = models.Manager()


class ChangePrices(models.Model):
    class Meta:
        verbose_name = 'Изменение цены'
        verbose_name_plural = 'Изменение цен'

    deal_price = models.ForeignKey(Deal, on_delete=models.PROTECT,
                                   related_name='deal_price_fk')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    date_change = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()


class TrackDeal(models.Model):
    class Meta:
        verbose_name = 'Отслеживаемая сделка'
        verbose_name_plural = 'Отслеживаемые сделки'
        unique_together = (('track_deal', 'who_track',),)

    track_deal = models.ForeignKey(Deal, on_delete=models.PROTECT, related_name='track_deal_fk')
    who_track = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='who_track_fk')

    objects = models.Manager()
