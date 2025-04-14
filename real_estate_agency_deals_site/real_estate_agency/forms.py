from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from real_estate_agency import models
from django.utils import timezone
from django import forms


class ReviewAgencyCreationForm(forms.ModelForm):
    class Meta:
        model = models.ReviewAgency
        fields = ('message', 'grade',)
        exclude = ('wrote_review',)

    grade = forms.DecimalField(widget=forms.NumberInput(attrs={'min': '0', 'max': '5', 'step': '0.1'}), label='Оценка')


class ReviewAgencyUpdateForm(forms.ModelForm):
    class Meta:
        model = models.ReviewAgency
        fields = ('message', 'grade',)

    grade = forms.DecimalField(widget=forms.NumberInput(attrs={'min': '0', 'max': '5', 'step': '0.1'}), label='Оценка')


class RealtorCreationForm(forms.ModelForm):
    class Meta:
        model = models.Realtor
        fields = ('last_name', 'first_name', 'patronymic', 'phone', 'email', 'price', 'license',)


class RealtorUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Realtor
        fields = ('last_name', 'first_name', 'patronymic', 'photo', 'experience', 'phone', 'email', 'price', 'license',)


class RealEstateForm(forms.Form):
    type = forms.ChoiceField(choices=models.RealEstate.RealEstateType.choices,
                             initial=models.RealEstate.RealEstateType.APARTMENT,
                             label='Тип недвижимости')
    # DataPlot
    data_plot_buildings = forms.BooleanField(required=False, label='Есть постройки')
    data_plot_communications = forms.BooleanField(required=False, label='Есть коммуникации')
    # end DataPlot
    # DataApartment
    data_apartment_number_storeys = forms.IntegerField(required=False, validators=[MinValueValidator(1)],
                                                       label='Количество этажей у дома')
    data_apartment_floor = forms.IntegerField(required=False, validators=[MinValueValidator(1)], label='Этаж')
    data_apartment_balcony = forms.BooleanField(required=False, label='Есть балкон')
    data_apartment_furniture = forms.BooleanField(required=False, label='Есть мебель')
    data_apartment_year_construction = forms.IntegerField(required=False, validators=[
        MinValueValidator(1900),
        MaxValueValidator(2**15),
    ], label='Год постройки')
    data_apartment_accident_rate = forms.BooleanField(required=False, label='Здание аварийное')
    data_apartment_room_type = forms.ChoiceField(required=False, choices=models.DataApartment.RoomType.choices,
                                                 initial=models.DataApartment.RoomType.OTHER, label='Тип комнаты')
    # end DataApartment
    # DataHouse
    data_house_number_storeys = forms.IntegerField(required=False, validators=[MinValueValidator(1)],
                                                   label='Количество этажей')
    data_house_house_area = forms.IntegerField(required=False, validators=[
        MinValueValidator(1),
    ], label='Площадь дома')
    data_house_year_construction = forms.IntegerField(required=False, validators=[
        MinValueValidator(1900),
        MaxValueValidator(2**15),
    ], label='Год постройки дома')
    data_house_garage = forms.BooleanField(required=False, label='Есть гараж')
    data_house_communications = forms.BooleanField(required=False, label='Есть коммуникации')
    # end DataHouse

    main_photo = forms.ImageField(required=False, validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    ], label='Главное фото')
    del_main_photo = forms.BooleanField(required=False, label='Удалить фото')
    square = forms.IntegerField(validators=[
        MinValueValidator(1),
    ], label='Общая площадь')
    about = forms.CharField(required=False, max_length=512, label='О недвижимости')

    have_address = forms.BooleanField(required=False, label='Добавить адрес (для шаблона недвижимости оставите пустым)')
    # Address
    city = forms.CharField(required=False, max_length=128, label='Город')
    district = forms.CharField(required=False, max_length=128, label='Район')
    street = forms.CharField(required=False, max_length=128, label='Улица')
    house = forms.IntegerField(required=False, validators=[
        MinValueValidator(1),
        MaxValueValidator(2**15),
    ], label='Номер дома')
    apartment = forms.IntegerField(required=False, validators=[
        MinValueValidator(1),
        MaxValueValidator(2 ** 15),
    ], label='Номер квартиры')
    # end Address

    def clean(self):
        cleaned_data = super().clean()
        have_address = cleaned_data.get('have_address')
        type_real_estate = int(cleaned_data.get('type'))

        if not have_address and type_real_estate == models.RealEstate.RealEstateType.PLOT:
            raise ValidationError('Шаблоном не может быть участок')

        if have_address:
            address_fields = ('city', 'street', 'house',)
            for field in address_fields:
                if not cleaned_data.get(field):
                    raise ValidationError(f'Поле "{self.fields[field].label}" обязательно при указании адреса')

        if type_real_estate == models.RealEstate.RealEstateType.PLOT:
            plot_fields = ('data_plot_buildings', 'data_plot_communications',)
            for field in plot_fields:
                if cleaned_data.get(field) is None:
                    raise ValidationError(f'Поле "{self.fields[field].label}" обязательно для участка')
        elif type_real_estate == models.RealEstate.RealEstateType.APARTMENT:
            apartment_fields = (
                'data_apartment_number_storeys', 'data_apartment_floor',
                'data_apartment_balcony', 'data_apartment_furniture',
                'data_apartment_year_construction', 'data_apartment_accident_rate',
                'data_apartment_room_type',
            )
            for field in apartment_fields:
                if cleaned_data.get(field) is None:
                    raise ValidationError(f'Поле "{self.fields[field].label}" обязательно для квартиры')
        elif type_real_estate == models.RealEstate.RealEstateType.HOUSE:
            house_fields = (
                'data_house_number_storeys', 'data_house_house_area',
                'data_house_year_construction', 'data_house_garage',
                'data_house_communications',
            )
            for field in house_fields:
                if cleaned_data.get(field) is None:
                    raise ValidationError(f'Поле "{self.fields[field].label}" обязательно для дома')

        return cleaned_data


class DealForm(forms.Form):
    title = forms.CharField(max_length=256, label='Заголовок')
    type = forms.ChoiceField(choices=models.Deal.DealType.choices,
                             initial=models.Deal.DealType.SALE,
                             label='Тип недвижимости')
    price = forms.DecimalField(max_digits=10, decimal_places=2, label='Цена')
    real_estate_deal_id = forms.IntegerField(label='Номер недвижимости')
    agent_username = forms.CharField(max_length=150, label='Логин агента недвижимости')

    # DataConstruction
    construction_company = forms.CharField(required=False, max_length=256, label='Название строительной компании')
    approximate_dates = forms.DurationField(required=False, validators=[MinValueValidator(timezone.timedelta(0))],
                                            label='Примерный срок строительства')
    project_document = forms.FileField(required=False, validators=[
        FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'odt']),
    ], label='Документ проекта')
    # end DataConstruction
    # DataRental
    price_housing_and_municipalities = forms.DecimalField(required=False, max_digits=10, decimal_places=2, label='Цена ЖКХ')
    prepayment = forms.DecimalField(required=False, max_digits=10, decimal_places=2, label='Предоплата')
    rental_period_days = forms.IntegerField(required=False, validators=[
        MinValueValidator(1),
        MaxValueValidator(2**15)
    ], label='Срок аренды в днях')
    # end DataRental

    def clean(self):
        cleaned_data = super().clean()
        type_deal = int(cleaned_data.get('type'))

        if type_deal == models.Deal.DealType.RENT:
            plot_fields = ('price_housing_and_municipalities', 'prepayment', 'rental_period_days',)
            for field in plot_fields:
                if cleaned_data.get(field) is None:
                    raise ValidationError(f'Поле "{self.fields[field].label}" обязательно для аренды')
        elif type_deal == models.Deal.DealType.CONSTRUCTION:
            apartment_fields = ('construction_company', 'approximate_dates','project_document',)
            for field in apartment_fields:
                if cleaned_data.get(field) is None:
                    raise ValidationError(f'Поле "{self.fields[field].label}" обязательно для строительства')

        return cleaned_data