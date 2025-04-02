# Generated by Django 5.1.7 on 2025-04-02 06:19

import datetime
import django.core.validators
import django.db.models.deletion
import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=128, verbose_name='Город')),
                ('district', models.CharField(blank=True, max_length=128, null=True, verbose_name='Район')),
                ('street', models.CharField(max_length=128, verbose_name='Улица')),
                ('apartment', models.SmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Квартира')),
            ],
            options={
                'verbose_name': 'Адрес',
                'verbose_name_plural': 'Адреса',
            },
        ),
        migrations.CreateModel(
            name='DataApartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_storeys', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество этажей')),
                ('floor', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Этаж')),
                ('balcony', models.BooleanField(verbose_name='Есть балкон')),
                ('furniture', models.BooleanField(verbose_name='Есть мебель')),
                ('year_construction', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1900)], verbose_name='Год постройки')),
                ('accident_rate', models.BooleanField(verbose_name='Здание аварийное')),
            ],
            options={
                'verbose_name': 'Данные квартиры',
                'verbose_name_plural': 'Данные квартир',
            },
        ),
        migrations.CreateModel(
            name='DataHouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_storeys', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество этажей')),
                ('house_area', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Площадь дома')),
                ('year_construction', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1900)], verbose_name='Год постройки дома')),
                ('garage', models.BooleanField(verbose_name='Есть гараж')),
                ('communications', models.BooleanField(verbose_name='Есть коммуникации')),
            ],
            options={
                'verbose_name': 'Данные дома',
                'verbose_name_plural': 'Данные домов',
            },
        ),
        migrations.CreateModel(
            name='DataPlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buildings', models.BooleanField(verbose_name='Есть постройки')),
                ('communications', models.BooleanField(verbose_name='Есть коммуникации')),
            ],
            options={
                'verbose_name': 'Данные участка',
                'verbose_name_plural': 'Данные участков',
            },
        ),
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, unique=True, verbose_name='Заголовок сделки')),
                ('type', models.SmallIntegerField(choices=[(0, 'Sale'), (1, 'Rent'), (2, 'Construction')], verbose_name='Тип сделки')),
                ('phone', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator('^\\+[1-9]\\d{1,14}$', 'Номер телефона должен быть в международном формате E.164 "+{от 2 до 15 цифр}"')], verbose_name='Номер телефона')),
                ('email', models.EmailField(max_length=254, verbose_name='Почта')),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Сделка',
                'verbose_name_plural': 'Сделки',
            },
            managers=[
                ('non_deleted', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PhotoRealEstate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='photos/real_estate/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name='Дополнительная фотография')),
            ],
            options={
                'verbose_name': 'Фото недвижимости',
                'verbose_name_plural': 'Фотографии недвижимости',
            },
        ),
        migrations.CreateModel(
            name='RealEstateAgency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, default='default/real_estate_agency.jpg', upload_to='photos/real_estate_agency/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name='Логотип')),
                ('slug_name', models.CharField(max_length=256, unique=True)),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Название организации')),
                ('INN', models.CharField(max_length=12, unique=True, validators=[django.core.validators.RegexValidator('^\\d{10,12}$')], verbose_name='ИНН')),
                ('about', models.CharField(blank=True, max_length=512, null=True, verbose_name='О агенстве')),
                ('date_registered', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Агенство недвижимости',
                'verbose_name_plural': 'Агентства недвижимости',
            },
        ),
        migrations.CreateModel(
            name='Realtor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=128, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=128, verbose_name='Имя')),
                ('patronymic', models.CharField(blank=True, max_length=128, null=True, verbose_name='Отчество')),
                ('photo', models.ImageField(blank=True, default='default/realtor.jpg', upload_to='photos/realtor/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name='Фото')),
                ('experience', models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('phone', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator('^\\+[1-9]\\d{1,14}$', 'Номер телефона должен быть в международном формате E.164 "+{от 2 до 15 цифр}"')], verbose_name='Номер телефона')),
                ('email', models.EmailField(max_length=254, verbose_name='Почта')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Цена услуг')),
                ('license', models.CharField(max_length=128, unique=True, verbose_name='Лицензия')),
            ],
            options={
                'verbose_name': 'Релайтер',
                'verbose_name_plural': 'Релайтеры',
            },
        ),
        migrations.CreateModel(
            name='ReviewAgency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=256, verbose_name='Отзыв')),
                ('grade', models.DecimalField(decimal_places=1, default=0.0, max_digits=2, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)], verbose_name='Оценка')),
                ('date_write', models.DateTimeField(auto_now_add=True)),
                ('change', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Отзыв агентства',
                'verbose_name_plural': 'Отзывы агенств',
            },
            managers=[
                ('non_deleted', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TrackDeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Отслеживаемая сделка',
                'verbose_name_plural': 'Отслеживаемые сделки',
            },
        ),
        migrations.CreateModel(
            name='DataRental',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_housing_and_municipalities', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Цена ЖКХ')),
                ('prepayment', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Предоплата')),
                ('rental_period_days', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Срок аренды')),
                ('rented', models.BooleanField(default=False, verbose_name='Арендуется')),
                ('deal_rental', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deal_rental_fk', to='real_estate_agency.deal')),
            ],
            options={
                'verbose_name': 'Данные аренды',
                'verbose_name_plural': 'Данные аренд',
            },
        ),
        migrations.CreateModel(
            name='DataConstruction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('construction_company', models.CharField(max_length=256, verbose_name='Строительная компания')),
                ('approximate_dates', models.DurationField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.timedelta(0))], verbose_name='Примерный срок строительства')),
                ('project_document', models.FileField(upload_to='documents/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'odt'])], verbose_name='Документ проекта')),
                ('deal_construction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deal_construction_fk', to='real_estate_agency.deal')),
            ],
            options={
                'verbose_name': 'Данные постройки',
                'verbose_name_plural': 'Данные построек',
            },
        ),
        migrations.CreateModel(
            name='ChangePrices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('date_change', models.DateTimeField(auto_now_add=True)),
                ('deal_price', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deal_price_fk', to='real_estate_agency.deal')),
            ],
            options={
                'verbose_name': 'Изменение цены',
                'verbose_name_plural': 'Изменение цен',
            },
        ),
        migrations.CreateModel(
            name='RealEstate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(choices=[(0, 'Apartment'), (1, 'House'), (2, 'Plot')], verbose_name='Тип недвижимости')),
                ('main_photo', models.ImageField(upload_to='photos/real_estate/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name='Главное фото')),
                ('square', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Общая площадь')),
                ('when_added', models.DateTimeField(auto_now_add=True)),
                ('about', models.CharField(blank=True, max_length=512, null=True, verbose_name='О недвижимости')),
                ('deleted', models.BooleanField(default=False)),
                ('address_real_estate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='address_real_estate_fk', to='real_estate_agency.address')),
            ],
            options={
                'verbose_name': 'Недвижимость',
                'verbose_name_plural': 'Недвижимости',
            },
            managers=[
                ('non_deleted', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='deal',
            name='real_estate_deal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='real_estate_deal_fk', to='real_estate_agency.realestate'),
        ),
    ]
