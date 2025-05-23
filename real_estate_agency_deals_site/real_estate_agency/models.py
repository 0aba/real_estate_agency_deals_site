from django.core.validators import FileExtensionValidator, RegexValidator, MinValueValidator, MaxValueValidator
from real_estate_agency_deals_site.settings import AUTH_USER_MODEL, LANGUAGE_CODE_TRANSLIT
from django.utils.text import slugify
from transliterate import translit
from django.utils import timezone
from django.db import models


class ReviewAgency(models.Model):
    class Meta:
        verbose_name = 'Отзыв агентства'
        verbose_name_plural = 'Отзывы агенств'
        ordering = ('-date_write',)

    wrote_review = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                                     related_name='wrote_review_fk')
    message = models.CharField(max_length=256, verbose_name='Отзыв')
    grade = models.DecimalField(max_digits=2, decimal_places=1, default=0.0, validators=[
        MinValueValidator(0.0),
        MaxValueValidator(5.0)
    ], verbose_name='Оценка')
    date_write = models.DateTimeField(auto_now_add=True)
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
    ], default='default/realtor.png',
       verbose_name='Фото')
    experience = models.SmallIntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Опыт (месяцев)')
    phone = models.CharField(validators=[
        RegexValidator(r'^[1-9]\d{1,14}$', 'Номер телефона должен быть в международном формате E.164'
                                                  ' "+{от 2 до 15 цифр}" (не надо вводить "+", только цифры)')
    ], max_length=15, verbose_name='Номер телефона')
    email = models.EmailField(verbose_name='Почта')
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0.0)], verbose_name='Цена услуг')
    license = models.CharField(max_length=128, unique=True, verbose_name='Лицензия')

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.photo:
            self.photo = 'default/realtor.png'
        super().save(*args, **kwargs)


class Address(models.Model):
    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    city = models.CharField(max_length=128, verbose_name='Город')
    district = models.CharField(null=True, blank=True, max_length=128, verbose_name='Район')
    street = models.CharField(max_length=128, verbose_name='Улица')
    house = models.SmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Номер дома')
    apartment = models.SmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1)],
                                         verbose_name='Квартира')

    objects = models.Manager()

    def __str__(self):
        address_parts = (
            f'Город {self.city}',
            f'Район {self.district}' if self.district else None,
            f'Улица {self.street}',
            f'Дом {self.house}',
            f'Кв. {self.apartment}' if self.apartment else None,
        )
        return ' '.join(filter(None, address_parts))


class RealEstate(models.Model):
    class Meta:
        verbose_name = 'Недвижимость'
        verbose_name_plural = 'Недвижимости'

    class RealEstateType(models.IntegerChoices):
        APARTMENT = 0, 'Квартира'
        HOUSE = 1, 'Дом'
        PLOT = 2, 'Участок'

    type = models.SmallIntegerField(choices=RealEstateType.choices, verbose_name='Тип недвижимости')
    main_photo = models.ImageField(blank=True, upload_to='photos/real_estate/%Y/%m/%d/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    ], default='default/real_estate.png',
       verbose_name='Главное фото')
    square = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Общая площадь')
    when_added = models.DateTimeField(auto_now_add=True)
    about = models.CharField(null=True, blank=True, max_length=512, verbose_name='О недвижимости')
    address_real_estate = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL,
                                            related_name='address_real_estate_fk')
    deleted = models.BooleanField(default=False)

    class NonDeletedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(deleted=False)

    non_deleted = NonDeletedManager()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.main_photo:
            self.main_photo = 'default/real_estate.png'

        super().save(*args, **kwargs)


class DataPlot(models.Model):
    class Meta:
        verbose_name = 'Данные участка'
        verbose_name_plural = 'Данные участков'

    real_estate_DP = models.OneToOneField(RealEstate, on_delete=models.PROTECT, related_name='real_estate_DP_fk')
    buildings = models.BooleanField(verbose_name='Есть постройки')
    communications = models.BooleanField(verbose_name='Есть коммуникации')

    objects = models.Manager()


class DataApartment(models.Model):
    class Meta:
        verbose_name = 'Данные квартиры'
        verbose_name_plural = 'Данные квартир'

    class RoomType(models.IntegerChoices):
        OTHER = 0, 'другое'
        COMMUNAL = 1, 'коммуналка'
        ONE_ROOM = 2, 'однокомнатная'
        TWO_ROOMS = 3, 'двухкомнатная'
        THREE_ROOMS = 4, 'трехкомнатная'
        FOUR_ROOMS = 5, 'четырехкомнатная'
        FOUR_PLUS_ROOMS = 6, 'четыре+ комнат'
        STUDIO = 7, 'студия'
        MAISONETTE = 8, 'мезонет'
        LOFT = 9, 'лофт'
        PENTHOUSE = 10, 'пентхаус'

    real_estate_DA = models.OneToOneField(RealEstate, on_delete=models.PROTECT, related_name='real_estate_DA_fk')
    number_storeys = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Количество этажей у дома')
    floor = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Этаж')
    balcony = models.BooleanField(verbose_name='Есть балкон')
    furniture = models.BooleanField(verbose_name='Есть мебель')
    year_construction = models.SmallIntegerField(validators=[MinValueValidator(1900)], verbose_name='Год постройки')
    accident_rate = models.BooleanField(verbose_name='Здание аварийное')
    room_type = models.SmallIntegerField(choices=RoomType.choices, default=RoomType.OTHER, verbose_name='Тип комнаты')

    objects = models.Manager()


class DataHouse(models.Model):
    class Meta:
        verbose_name = 'Данные дома'
        verbose_name_plural = 'Данные домов'

    real_estate_DH = models.ForeignKey(RealEstate, on_delete=models.PROTECT, related_name='real_estate_DH_fk')
    number_storeys = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Количество этажей')
    house_area = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Площадь дома')
    year_construction = models.SmallIntegerField(validators=[MinValueValidator(1900)], verbose_name='Год постройки дома')
    garage = models.BooleanField(verbose_name='Есть гараж')
    communications = models.BooleanField(verbose_name='Есть коммуникации')

    objects = models.Manager()


class Deal(models.Model):
    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'

    class DealType(models.IntegerChoices):
        SALE = 0, 'Продажа'
        RENT = 1, 'Аренда'
        CONSTRUCTION = 2, 'Строительство'

    class DealCompletedType(models.IntegerChoices):
        CLIENT_SEARCH = 0, 'Поиск клиента'
        IN_PROGRESS = 1, 'В процессе совершения'
        SUCCESS = 2, 'Успешно совершена'
        REJECTED = 3, 'Отклонена сделка'

    title_slug = models.CharField(max_length=256, unique=True)
    title = models.CharField(max_length=256, unique=True, verbose_name='Заголовок сделки')
    type = models.SmallIntegerField(choices=DealType.choices, default=DealType.SALE, verbose_name='Тип сделки')
    current_price = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)], verbose_name='Текущая цена')
    date_create = models.DateTimeField(auto_now_add=True)
    real_estate_deal = models.ForeignKey(RealEstate, on_delete=models.PROTECT, related_name='real_estate_deal_fk')
    agent = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='agent_fk')
    deal_with = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, related_name='deal_with_fk')
    completed_type = models.SmallIntegerField(choices=DealCompletedType.choices, default=DealCompletedType.CLIENT_SEARCH, verbose_name='Тип сделки')
    completion_document = models.FileField(null=True, upload_to='documents/deal/completion/%Y/%m/%d/', validators=[
        FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'odt']),
    ], verbose_name='Документ сделки')
    deleted = models.BooleanField(default=False)

    class NonDeletedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(deleted=False)

    non_deleted = NonDeletedManager()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        self.title_slug = slugify(translit(self.title, LANGUAGE_CODE_TRANSLIT, reversed=True))
        super().save(*args, **kwargs)


class DataConstruction(models.Model):
    class Meta:
        verbose_name = 'Данные постройки'
        verbose_name_plural = 'Данные построек'

    deal_construction = models.ForeignKey(Deal, on_delete=models.PROTECT, related_name='deal_construction_fk')
    construction_company = models.CharField(max_length=256, verbose_name='Строительная компания')
    approximate_dates = models.DurationField(null=True, blank=True,
                                             validators=[MinValueValidator(timezone.timedelta(0))],
                                             verbose_name='Примерный срок строительства')
    project_document = models.FileField(upload_to='documents/deal/project/%Y/%m/%d/', validators=[
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
    rental_period_days = models.SmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Срок аренды в днях')

    objects = models.Manager()


class ChangePrices(models.Model):
    class Meta:
        verbose_name = 'Изменение цены'
        verbose_name_plural = 'Изменение цен'

    deal_price = models.ForeignKey(Deal, on_delete=models.PROTECT,
                                   related_name='deal_price_fk')
    price = models.DecimalField(validators=[MinValueValidator(0)], max_digits=10, decimal_places=2, verbose_name='Цена')
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
